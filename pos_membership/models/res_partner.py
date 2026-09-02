# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_is_valid = fields.Boolean(
        string="Adhesion valide",
        compute="_compute_membership_is_valid",
        store=True,
        help="Vrai si le statut d'adhesion du partenaire est considere comme"
        " membre (cf. res.partner._membership_member_states()) : sert au"
        " code couleur rouge/vert dans le PoS.",
    )

    @api.depends("membership_state")
    def _compute_membership_is_valid(self):
        member_states = self._membership_member_states()
        for partner in self:
            partner.membership_is_valid = partner.membership_state in member_states

    @api.model
    def _load_pos_data_fields(self, config):
        params = super()._load_pos_data_fields(config)
        return params + [
            "membership_state",
            "membership_is_valid",
            "membership_stop",
            "membership_category_ids",
        ]
