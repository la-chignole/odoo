# -*- coding: utf-8 -*-
from odoo import api, models


class MembershipCategory(models.Model):
    _name = "membership.membership_category"
    _inherit = ["membership.membership_category", "pos.load.mixin"]

    @api.model
    def _load_pos_data_fields(self, config):
        return ["id", "name"]
