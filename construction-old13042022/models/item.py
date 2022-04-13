
from odoo import models, fields, api

class Item(models.Model):
    _name = 'product.item'
    name = fields.Char("Name",required=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure",required=True)
