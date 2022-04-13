from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'construction.contract'
    contract_num = fields.Char("Contract Number")
    note = fields.Html("Notes")

