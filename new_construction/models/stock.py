from odoo import fields, models, api


class Picking(models.Model):
    _inherit = 'stock.picking'
    project_id = fields.Many2one("project.project", string="Project")


