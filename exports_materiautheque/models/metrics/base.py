# -*- coding: utf-8 -*-
"""A metric is a small function computing one statistic from Odoo data.

Registering one is the only thing a new report ever needs: add a function
below (or in a new file under ``models/metrics/``, then import it from
``models/metrics/__init__.py``), decorate it with
``@register_metric("some_key")``, and any template that types
``{{some_key}}`` in a cell will pick it up -- nothing else in this module
changes.

A metric always takes ``env`` first, then keyword-only parameters. The
wizard/CLI only ever supply ``date_from``/``date_to`` -- there is no
run-time tag/PoS-category filter at all. A metric that wants to filter by
tag or PoS category still declares ``tag_ids=None``/``pos_categ_ids=None``
params (defaulting to "no filter" when nobody sets them), but the *only*
way either ever gets a value is a template placeholder naming it directly,
e.g. ``{{key["Mat 1","Mat 2"]}}`` -- see
``utils/xlsx_template_filler.py``'s module docstring for the full grammar.
This is deliberate: a template is meant to be written once and never
change what it reports -- the date range is its only run-time input.
``compute_metrics`` resolves a bracket's names to ids and calls the metric
once per distinct filter. A list-returning ("detail") metric referenced
through a ``.field`` accessor with more than one name must return its rows
**in the same order the ids were given** (already true for anything that
loops ``for x in env[...].browse(ids):`` -- browsing a given id list
preserves that order) -- a ``.field``-multi placeholder addresses a row by
position, not by matching a field's value. Accept ``**kw`` in every metric
regardless, since the same call site feeds every metric a template asks
for, whatever model each one actually reads.
"""

from ...utils.xlsx_template_filler import TemplateError

_METRIC_REGISTRY = {}

# Filter axes a template placeholder can name -- kept in sync with
# ``utils/xlsx_template_filler.py``'s ``VALID_AXES``. Maps an axis to the
# (model, name field) used to resolve a name to an id, and to the kwarg a
# metric function reads it as.
_AXIS_MODELS = {
    "tag": ("product.tag", "name"),
    "pos_categ": ("pos.category", "name"),
}
_AXIS_PARAM = {
    "tag": "tag_ids",
    "pos_categ": "pos_categ_ids",
}


def register_metric(key):
    """Function decorator registering a metric under ``key``."""

    def decorator(func):
        if key in _METRIC_REGISTRY:
            raise ValueError("Metric '%s' is already registered" % key)
        _METRIC_REGISTRY[key] = func
        return func

    return decorator


def get_metric(key):
    return _METRIC_REGISTRY.get(key)


def registered_metric_keys():
    return sorted(_METRIC_REGISTRY)


def _resolve_axis_names(env, axis, names):
    """Resolve ``names`` (tag/category names typed in a template) to ids.

    Returns ``(ids, missing_names)`` rather than raising, so a caller can
    choose to fail on the first problem (:func:`compute_metrics`) or collect
    every one (:func:`validate_calls`). ``ids`` is given in the same order
    as ``names`` -- see this module's docstring on why that order matters.
    """
    model_name, field_name = _AXIS_MODELS[axis]
    records = env[model_name].search([(field_name, "in", names)])
    id_by_name = {rec[field_name]: rec.id for rec in records}
    ids, missing = [], []
    for name in names:
        if name in id_by_name:
            ids.append(id_by_name[name])
        else:
            missing.append(name)
    return ids, missing


def compute_metrics(env, calls, **base_params):
    """Compute ``{canonical_key: value}`` for every metric call a template
    needs (``calls`` is ``TemplateFiller.required_calls()``'s result).

    ``base_params`` (just the wizard/CLI's ``date_from``/``date_to``) is
    passed as-is to every metric, except for whichever axes a given call's
    own bracket names -- those set that one call's value for that axis (a
    metric never gets a tag/PoS-category filter any other way). Each
    metric reads only the parameters it needs and ignores the rest, so a
    single generic call site works for every template.
    """
    result = {}
    for call in calls:
        func = get_metric(call.base_key)
        if func is None:
            raise TemplateError(
                "Unknown metric '%s' (sheet '%s', row %s) -- no function "
                "registered under that key in models/metrics/"
                % (call.base_key, call.sheet, call.row)
            )
        params = dict(base_params)
        for axis, names in call.axes.items():
            ids, missing = _resolve_axis_names(env, axis, names)
            if missing:
                raise TemplateError(
                    '%s "%s" not found (sheet \'%s\', row %s)'
                    % (axis, '", "'.join(missing), call.sheet, call.row)
                )
            params[_AXIS_PARAM[axis]] = ids
        result[call.canonical_key] = func(env, **params)
    return result


def validate_calls(env, calls):
    """Human-readable problems (unknown metric, unresolvable name) across
    every call, without raising -- for showing a template's issues all at
    once when it's uploaded, rather than one at a time on each Generate."""
    problems = []
    for call in calls:
        if get_metric(call.base_key) is None:
            problems.append(
                "unknown metric '%s' (sheet '%s', row %s)"
                % (call.base_key, call.sheet, call.row)
            )
            continue
        for axis, names in call.axes.items():
            _ids, missing = _resolve_axis_names(env, axis, names)
            if missing:
                problems.append(
                    '%s "%s" not found (sheet \'%s\', row %s)'
                    % (axis, '", "'.join(missing), call.sheet, call.row)
                )
    return problems


def products_matching_tags(env, tag_ids):
    """``product.product`` recordset carrying at least one of ``tag_ids``.

    Shared by every metric that filters by ``product.tag`` -- expected to
    be the axis used the most -- regardless of which document model (PoS
    lines, stock moves, ...) a given metric actually reads from. A falsy
    ``tag_ids`` means "no tag filter", returning every product.
    """
    product_model = env['product.product']
    if not tag_ids:
        return product_model.search([])
    return product_model.search([('all_product_tag_ids', 'in', tag_ids)])


def pos_line_weight(line):
    """Best-effort real weight (kg) of one sold ``pos.order.line``.

    The ``pos_weight`` module (see repo root) stores a human-declared (or,
    for products sold by weight, auto-filled) ``weight`` on the line --
    that value is already the weight of the *entire* line, not a per-unit
    weight, so it must never be multiplied by the quantity. Only falls back
    to computing it from the quantity (UoM category = kg) when that field
    is empty, e.g. a line sold before ``pos_weight`` was installed, or
    created through a route that bypasses its frontend.
    """
    if 'weight' in line._fields and line.weight:
        return line.weight
    env = line.env
    kg_category = env.ref('uom.product_uom_categ_kgm', raise_if_not_found=False)
    if kg_category and line.product_uom_id.category_id == kg_category:
        return line.qty / (line.product_uom_id.factor or 1.0)
    return 0.0
