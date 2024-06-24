# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint
from odoo.exceptions import ValidationError


class HrLateRuleLine(models.Model):
    _inherit = 'hr.late.rule.line'

    type = [
        ('fix', 'Fixed'),
        ('rate', 'Rate'),
        ('percentage', 'Percentage'),
    ]

    type = fields.Selection(string="Type", selection=type, required=True, )
    percentage = fields.Float("Percentage")


class HrDiffRuleLine(models.Model):
    _inherit = 'hr.diff.rule.line'

    type = [
        ('fix', 'Fixed'),
        ('rate', 'Rate'),
        ('percentage', 'Percentage'),
    ]

    type = fields.Selection(string="Type", selection=type, required=True, )
    percentage = fields.Float("Percentage")

