# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    portal_user_id = fields.Many2one('res.users',domain="[(1,'=',1)]")




