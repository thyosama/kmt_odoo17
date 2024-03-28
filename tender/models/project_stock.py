from odoo import models, fields, api





class sale_order(models.Model):
    _inherit = 'sale.order'
    project_id= fields.Many2one(comodel_name='project.project', string='Project',)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    project_id= fields.Many2one(comodel_name='project.project', string='Project',related="order_id.project_id",store=True)














