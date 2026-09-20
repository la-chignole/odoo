# -*- coding: utf-8 -*-
from .base import register_metric, products_matching_tags, pos_line_weight

_SOLD_STATES = ('paid', 'done')


def _pos_lines_domain(env, date_from=None, date_to=None, tag_ids=None,
                       pos_categ_ids=None, **kw):
    domain = [('order_id.state', 'in', list(_SOLD_STATES))]
    if date_from:
        domain.append(('order_id.date_order', '>=', date_from))
    if date_to:
        domain.append(('order_id.date_order', '<=', date_to))
    if pos_categ_ids:
        domain.append(('product_id.pos_categ_ids', 'in', pos_categ_ids))
    if tag_ids:
        products = products_matching_tags(env, tag_ids)
        domain.append(('product_id', 'in', products.ids))
    return domain


@register_metric('pos.recette_categorie')
def recette_categorie(env, **params):
    """Sum of paid PoS receipts (tax included), optionally filtered by PoS
    category and/or product tag over a date range."""
    lines = env['pos.order.line'].search(_pos_lines_domain(env, **params))
    return sum(lines.mapped('price_subtotal_incl'))


@register_metric('pos.unites_vendues')
def unites_vendues(env, **params):
    """Number of units sold matching the same filters -- e.g. "how many
    garden tools were sold this month"."""
    lines = env['pos.order.line'].search(_pos_lines_domain(env, **params))
    return sum(lines.mapped('qty'))


@register_metric('stock.poids_par_tag_detail')
def poids_par_tag_detail(env, tag_ids=None, **params):
    """One row per selected product tag, with the weight (kg) actually sold
    for that tag over the date range -- feeds a ``{{rows:...}}`` block for a
    "weight sold, broken down by tag" table. Falls back to every existing
    tag when none is selected in the wizard.

    Reads ``pos.order.line`` rather than stock moves: PoS sales don't
    necessarily create a delivery picking, but the ``pos_weight`` module
    always records the sold weight directly on the line (human-declared, or
    auto-filled for products sold by weight) -- see ``pos_line_weight``.
    Kept under the ``stock.`` key namespace for backward compatibility with
    existing templates."""
    tags = env['product.tag'].browse(tag_ids) if tag_ids else env['product.tag'].search([])
    rows = []
    for tag in tags:
        lines = env['pos.order.line'].search(_pos_lines_domain(
            env, tag_ids=tag.ids, **params))
        rows.append({
            'tag': tag.name,
            'weight': round(sum(pos_line_weight(line) for line in lines), 2),
        })
    return rows
