# -*- coding: utf-8 -*-

import datetime
from pytz import timezone, all_timezones
import logging
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    one_days_login = fields.Boolean(string="Attends One Days", config_parameter='base_setup.one_days_login')

