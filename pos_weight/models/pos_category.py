# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosCategory(models.Model):
    _inherit = "pos.category"

    hide_weight_in_pos = fields.Boolean(
        string="Poids non requis en PoS",
        help="Si actif, les produits de cette categorie PoS n'affichent pas"
        " le suivi de poids dans le point de vente (utile pour les"
        " prestations de service, par exemple).",
    )

    @api.model
    def _load_pos_data_fields(self, config):
        params = super()._load_pos_data_fields(config)
        return params + ["hide_weight_in_pos"]
