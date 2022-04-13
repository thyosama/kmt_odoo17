from odoo import fields, models, api

class Project(models.Model):
    _inherit = 'project.project'
    cost_line_ids = fields.One2many('project.cost.line','project_id')
class ModelName(models.Model):
    _name = 'project.cost.line'
    product_id =  fields.Many2one("product.product",string="product")
    qty = fields.Float("Quantity")
    name = fields.Char()
    price_unit = fields.Float("Price Unit ")
    total = fields.Float(compute="_get_total")
    project_id = fields.Many2one("project.project")
    @api.depends('price_unit','qty')
    def _get_total(self):
        for rec in self:
            rec.total = rec.price_unit*rec.qty
