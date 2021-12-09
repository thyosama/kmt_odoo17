from odoo import models, fields, api


class contract(models.Model):
    _name = 'construction.contract.user'

    name = fields.Char("Name")
    account_id = fields.Many2one("account.account",string="Parent Account")
    counterpart_account_id = fields.Many2one("account.account",string="partner Account")
    type = fields.Selection([('owner','Owner'),('supconstractor','sub contractor')],string="Type")