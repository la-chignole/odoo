# -*- coding: utf-8 -*-
"""Accounting export ("Export Comptable Mensuel") -- two metrics sharing
one computation, grouped either by day or by month, each broken down by
payment method and by what was sold.

Business rules baked into this metric (decided when it was written, not
left open -- adjust here, not in the template, if any of these change):

- Three revenue buckets per payment method: "Adhésion" (product is in the
  PoS category named exactly "Adhésion"), "Services" (remaining lines
  whose product type is 'service' -- checked *after* Adhésion, since
  membership products are themselves typed 'service' in this database),
  "Produits" (everything else, i.e. 'consu'/'combo' lines). Their sum is
  "Recette Totale".
- "Encaissé réel" is a payment's own amount -- the actual amount collected
  via that method, meant for reconciling against a physical cash count.
  The three Recette columns split the *same order's* line revenue
  proportionally across its payment(s) by each payment's share of the
  order's total: exact for the common one-payment-per-order case, an
  approximation for a split-tender order.
- "Écart" is Encaissé réel minus Recette Totale -- normally zero (a
  payment's amount and its share of the order's categorized lines should
  match), but not guaranteed to be: an order-level rounding adjustment or
  a discount not reflected per line lands in Encaissé réel without ever
  being attributed to a category, so it shows up here instead of silently
  vanishing. A day/month with a non-zero Écart is worth checking by hand.
- Payment methods are matched by name (Espèces/Chèque/Carte) -- a method
  that doesn't exist yet in a given database just reports zero everywhere,
  and starts working the moment it's created, no code change needed. Any
  *other* payment method (e.g. "Compte client") isn't counted anywhere,
  including the Total columns -- only these three feed this report.
- "Sorties Achat"/"Sorties Banque" from the original report mockup are
  deliberately not included: nothing in this database represents a cash
  purchase payout or a till-to-bank transfer yet. The day sheet still has
  manual columns for them (filled by hand, not by this metric).
"""

from collections import defaultdict

from .base import register_metric

_PAYMENT_METHODS = [
    ("Espèces", "especes"),
    ("Chèque", "cheque"),
    ("Carte", "carte"),
]
# Accumulated straight from orders/payments; "ecart" and "recette_totale"
# are derived from these at output time, not tracked separately (see
# _derive_output).
_RAW_FIELDS = ("encaisse_reel", "recette_adhesion", "recette_services", "recette_produits")


def _derive_output(raw):
    """One payment method's (or the row's total) accumulated raw numbers
    -> the 6 output fields, rounded only here so summing totals from raw,
    unrounded per-method numbers doesn't compound rounding error."""
    totale = raw["recette_adhesion"] + raw["recette_services"] + raw["recette_produits"]
    return {
        "encaisse_reel": round(raw["encaisse_reel"], 2),
        "ecart": round(raw["encaisse_reel"] - totale, 2),
        "recette_totale": round(totale, 2),
        "recette_adhesion": round(raw["recette_adhesion"], 2),
        "recette_services": round(raw["recette_services"], 2),
        "recette_produits": round(raw["recette_produits"], 2),
    }


def _compute_buckets(env, date_from, date_to, group_key):
    """Shared computation for both metrics below: ``{group_key(order):
    {payment_key: {raw_field: amount}}}`` -- everything except how orders
    are grouped into rows is identical between "by day" and "by month"."""
    domain = [("state", "in", ("paid", "done"))]
    if date_from:
        domain.append(("date_order", ">=", date_from))
    if date_to:
        domain.append(("date_order", "<=", date_to))
    orders = env["pos.order"].search(domain)

    adhesion_categ = env["pos.category"].search([("name", "=", "Adhésion")], limit=1)
    method_key_by_id = {}
    for name, key in _PAYMENT_METHODS:
        method = env["pos.payment.method"].search([("name", "=", name)], limit=1)
        if method:
            method_key_by_id[method.id] = key

    groups = defaultdict(lambda: {
        key: {field: 0.0 for field in _RAW_FIELDS}
        for _name, key in _PAYMENT_METHODS
    })

    for order in orders:
        bucket = groups[group_key(order)]

        adhesion_total = service_total = produit_total = 0.0
        for line in order.lines:
            amount = line.price_subtotal_incl
            product = line.product_id
            if adhesion_categ and adhesion_categ.id in product.pos_categ_ids.ids:
                adhesion_total += amount
            elif product.type == "service":
                service_total += amount
            else:
                produit_total += amount

        order_total = order.amount_total or 0.0
        for payment in order.payment_ids:
            key = method_key_by_id.get(payment.payment_method_id.id)
            if key is None:
                continue
            ratio = (payment.amount / order_total) if order_total else 0.0
            bucket[key]["encaisse_reel"] += payment.amount
            bucket[key]["recette_adhesion"] += ratio * adhesion_total
            bucket[key]["recette_services"] += ratio * service_total
            bucket[key]["recette_produits"] += ratio * produit_total

    return groups


def _rows_from_buckets(groups):
    """``{group: {payment_key: raw}}`` -> the list of row dicts a template
    reads, one per group, sorted by the group key (a date either way)."""
    rows = []
    for group in sorted(groups):
        bucket = groups[group]
        row = {"date": group}
        totals_raw = {field: 0.0 for field in _RAW_FIELDS}
        for _name, key in _PAYMENT_METHODS:
            raw = bucket[key]
            for field in _RAW_FIELDS:
                totals_raw[field] += raw[field]
            for out_field, value in _derive_output(raw).items():
                row["%s_%s" % (key, out_field)] = value
        for out_field, value in _derive_output(totals_raw).items():
            row["total_%s" % out_field] = value
        rows.append(row)
    return rows


@register_metric("compta.export_comptable_par_jour")
def export_comptable_par_jour(env, date_from=None, date_to=None, **kw):
    groups = _compute_buckets(env, date_from, date_to, group_key=lambda order: order.date_order.date())
    return _rows_from_buckets(groups)


@register_metric("compta.export_comptable_par_mois")
def export_comptable_par_mois(env, date_from=None, date_to=None, **kw):
    """Same computation as the daily metric, grouped by month instead --
    ``date`` is the first day of each month (a real date, so a template
    can give that column a "mmmm yyyy" number format instead of showing
    a full date)."""
    groups = _compute_buckets(
        env, date_from, date_to,
        group_key=lambda order: order.date_order.date().replace(day=1),
    )
    return _rows_from_buckets(groups)
