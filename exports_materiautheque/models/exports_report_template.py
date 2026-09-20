# -*- coding: utf-8 -*-
import base64
import binascii
import logging
import os

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path
from odoo.tools.translate import _

from .metrics.base import compute_metrics, validate_calls
from ..utils.xlsx_template_filler import TemplateError, TemplateFiller

_logger = logging.getLogger(__name__)

#: Fields that make a record "the template" (as opposed to bookkeeping like
#: `active`) -- locked once `is_builtin` is set, on any record already
#: built-in, from any caller except this model's own sync (see write()).
_BUILTIN_LOCKED_FIELDS = {
    'xlsx_template', 'xlsx_template_filename', 'name', 'is_builtin', 'builtin_source',
}


class ExportsReportTemplate(models.Model):
    _name = 'exports.report.template'
    _description = "Export report template"
    _order = 'name'

    name = fields.Char(required=True)
    xlsx_template = fields.Binary(
        string="Template (.xlsx)", required=True, attachment=True,
        help="An .xlsx file with {{ }} placeholders -- see "
             "doc/template_authoring.md for how to write one.",
    )
    xlsx_template_filename = fields.Char(string="Filename")
    is_builtin = fields.Boolean(
        default=False, readonly=True,
        help="Shipped by the module as a ready-to-use report, rather than "
             "uploaded by a user. Synced automatically from every .xlsx in "
             "the module's data/templates/ folder on every server restart "
             "-- edit the file there, not this record: a built-in "
             "template's content can't be changed from here.",
    )
    builtin_source = fields.Char(
        readonly=True, copy=False,
        help="Filename in data/templates/ this built-in was synced from. "
             "Empty for a template someone uploaded themselves.",
    )
    active = fields.Boolean(default=True)
    required_metric_keys = fields.Char(
        compute='_compute_required_keys', string="Metrics used",
        help="Metric keys this template's {{ }} placeholders reference, "
             "shown for information -- generating the export is what "
             "actually checks that every one of them is registered. "
             "Prefixed with a warning if a {{key[\"Name\"]}} bracket names "
             "a tag/category that doesn't exist.",
    )
    required_block_keys = fields.Char(
        compute='_compute_required_keys', string="Row blocks used",
    )

    @api.depends('xlsx_template')
    def _compute_required_keys(self):
        # This runs as an onchange the moment a file is picked in the
        # widget, before the record is even saved -- a bad file must show
        # up as a value in these two fields, never as a crashed form.
        for template in self:
            if not template.xlsx_template:
                template.required_metric_keys = ''
                template.required_block_keys = ''
                continue
            try:
                content = base64.b64decode(template.xlsx_template)
                metric_keys, block_keys = TemplateFiller.required_keys(content)
                calls = TemplateFiller.required_calls(content)
            except (TemplateError, binascii.Error) as exc:
                # binascii.Error means xlsx_template itself isn't valid
                # base64 (a corrupted/truncated upload) -- this compute
                # runs for every row a list view reads, so letting it
                # raise would break the *entire* list, not just this one
                # record's row.
                template.required_metric_keys = _("⚠ %s", exc)
                template.required_block_keys = ''
                continue
            problems = validate_calls(template.env, calls)
            metric_display = ', '.join(sorted(metric_keys))
            if problems:
                metric_display = "⚠ %s" % '; '.join(problems) + (
                    " -- %s" % metric_display if metric_display else ""
                )
            template.required_metric_keys = metric_display
            template.required_block_keys = ', '.join(sorted(block_keys))

    def _register_hook(self):
        super()._register_hook()
        self.sudo()._sync_builtin_templates()

    def _sync_builtin_templates(self):
        """Create/refresh one ``exports.report.template`` per .xlsx file
        under this module's data/templates/ -- called on every server
        restart (see _register_hook), so shipping a new built-in report is
        "drop the file there", no XML record needed. Safe to always
        overwrite an existing one's content: built-ins can't be edited any
        other way (see write()/create() below), so there's never a local
        customization here to protect.
        """
        module_path = get_module_path('exports_materiautheque')
        templates_dir = os.path.join(module_path or '', 'data', 'templates')
        if not module_path or not os.path.isdir(templates_dir):
            return
        for filename in sorted(os.listdir(templates_dir)):
            if not filename.lower().endswith('.xlsx'):
                continue
            try:
                # A failed query (e.g. this file's sync hitting a schema
                # that isn't migrated yet) poisons the whole surrounding
                # transaction in PostgreSQL -- catching the Python
                # exception alone doesn't stop every later query in this
                # same registry load from failing too. A savepoint makes
                # one file's failure roll back only its own work.
                with self.env.cr.savepoint():
                    with open(os.path.join(templates_dir, filename), 'rb') as f:
                        content = base64.b64encode(f.read())
                    values = {
                        'xlsx_template': content,
                        'xlsx_template_filename': filename,
                    }
                    existing = self.search([('builtin_source', '=', filename)], limit=1)
                    if existing:
                        existing.with_context(builtin_sync=True).write(values)
                    else:
                        values.update(
                            name=os.path.splitext(filename)[0].replace('_', ' ').title(),
                            is_builtin=True,
                            builtin_source=filename,
                        )
                        self.with_context(builtin_sync=True).create(values)
            except Exception:
                _logger.exception("Could not sync built-in template '%s'", filename)

    def write(self, vals):
        if not self.env.context.get('builtin_sync') and _BUILTIN_LOCKED_FIELDS & set(vals):
            if any(template.is_builtin for template in self):
                raise UserError(_(
                    "Built-in templates are shipped with the module and can't "
                    "be edited -- change the .xlsx in data/templates/ and "
                    "restart the server instead."
                ))
        return super().write(vals)

    def create(self, vals_list):
        if not self.env.context.get('builtin_sync'):
            for vals in vals_list:
                vals.pop('is_builtin', None)
                vals.pop('builtin_source', None)
        return super().create(vals_list)

    def action_generate(self, params):
        """Fill this template against ``params`` (the wizard's values) and
        return the generated .xlsx file, base64-encoded -- like any other
        Odoo binary payload, so it survives XML-RPC marshalling (raw bytes
        aren't valid UTF-8 and this build's XML-RPC controller assumes they
        are)."""
        self.ensure_one()
        if not self.xlsx_template:
            raise UserError(_("This template has no file to fill."))
        try:
            content = base64.b64decode(self.xlsx_template)
            calls = TemplateFiller.required_calls(content)
            metrics = compute_metrics(self.env, calls, **params)
            return base64.b64encode(TemplateFiller(content).fill(metrics))
        except (TemplateError, binascii.Error) as exc:
            raise UserError(str(exc)) from exc
