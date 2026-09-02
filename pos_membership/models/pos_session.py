# -*- coding: utf-8 -*-
from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _load_pos_data_models(self, config):
        models_list = super()._load_pos_data_models(config)
        return models_list + ["membership.membership_category"]
