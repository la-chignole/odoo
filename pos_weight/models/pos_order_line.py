# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    weight = fields.Float(
        string="Poids (kg)",
        digits=(12, 3),
        help="Poids reel de la ligne, utilise pour les rapports de matieres."
        " Pour les produits vendus au kg, il est deduit automatiquement de"
        " la quantite si non renseigne manuellement.",
    )

    @api.model
    def _load_pos_data_fields(self, config):
        params = super()._load_pos_data_fields(config)
        return params + ["weight"]
