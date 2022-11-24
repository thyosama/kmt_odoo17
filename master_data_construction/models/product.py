from odoo import fields, models, api


class Product(models.Model):
    _inherit = 'product.template'
    expense = fields.Boolean('Expense')
    material = fields.Boolean('Material')
    labour = fields.Boolean('Labour')
    equipment = fields.Boolean('Equipment')
    indirect_cost = fields.Boolean('indirect Cost')
    subContractor = fields.Boolean('SubContractor')