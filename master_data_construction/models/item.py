
from odoo import models, fields, api

class Item(models.Model):
    _name = 'product.item'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name = fields.Char("Name",required=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure",required=True)
    related_job = fields.Many2one("tender.related.job")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
