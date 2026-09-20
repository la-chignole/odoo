# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ExportsExportWizard(models.TransientModel):
    _name = 'exports.export.wizard'
    _description = "Generate an export from a template"

    template_id = fields.Many2one(
        'exports.report.template', required=True, string="Template",
        domain=[('active', '=', True)],
    )
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    @api.model
    def default_get(self, fields_list):
        # A one-click built-in report's menu entry (views/menu.xml) sets
        # 'default_builtin_source' in its action context instead of
        # 'default_template_id' directly, naming the shipped .xlsx's
        # filename rather than a specific record id -- since a built-in
        # template's own id isn't stable/knowable from XML (it's created
        # by exports.report.template's filesystem sync, not a <record>),
        # this resolves it by that filename instead.
        values = super().default_get(fields_list)
        builtin_source = self.env.context.get('default_builtin_source')
        if builtin_source and 'template_id' in fields_list and not values.get('template_id'):
            template = self.env['exports.report.template'].search(
                [('builtin_source', '=', builtin_source)], limit=1,
            )
            if template:
                values['template_id'] = template.id
        return values

    def action_generate(self):
        self.ensure_one()
        # The date range is the only thing this screen ever decides -- any
        # tag/PoS-category filtering a template needs is fixed inside the
        # template itself (a {{key["Name"]}} bracket), not chosen here, so
        # the same template always produces the same report shape.
        params = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        content_b64 = self.template_id.action_generate(params)
        attachment = self.env['ir.attachment'].create({
            'name': '%s.xlsx' % (self.template_id.name or 'export'),
            'type': 'binary',
            'datas': content_b64,
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
