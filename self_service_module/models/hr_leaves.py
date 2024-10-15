# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _inherit = 'hr.leave'

    from_website = fields.Boolean(default=False)




