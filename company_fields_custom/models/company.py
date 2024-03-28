# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    show_taxes = fields.Boolean()
    show_cost_per_unit = fields.Boolean()
