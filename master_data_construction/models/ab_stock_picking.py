from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one(comodel_name='project.project')


class StockMove(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one(comodel_name='project.project', string='Project', related="picking_id.project_id",
                                 store=True)
    # job_cost_id = fields.Many2one('construction.job.cost', 'Job Cost')
    item_ids = fields.Many2many('product.item', "item_id","line_ids",string='Item',compute='_get_item_list')
    product_ids = fields.Many2many('product.product', "product_id","line_ids",string='Product',compute='_get_product_list')
    item = fields.Many2one('product.item', string='Item', domain="[('id','in',item_ids)]")
    # product_id = fields.Many2one("product.product",string="Product",domain="[('id','in',product_ids)]")
    @api.depends('project_id','item')
    def _get_product_list(self):
        for rec in self:


            ids, domain = [], []
            rec.product_ids=[]
            if rec.project_id:
                domain.append(('id', '=', rec.project_id.id))
            if rec.item:
                domain.append(('item', '=', rec.item.id))

            pro = self.env['construction.job.cost'].search(domain)
            for mat in pro.material_ids:

                rec.product_ids=[(4,mat.product_id.id)]

            for mat in pro.labour_ids:
                rec.product_ids=[(4,mat.product_id.id)]
            for mat in pro.equipment_ids:
                rec.product_ids=[(4,mat.product_id.id)]
    @api.depends('project_id')
    def _get_item_list(self):
        ids=[]
        for rec in self:
            rec.item_ids=[]
            if rec.project_id:
                pro = self.env['project.project'].search([('id', '=', rec.project_id.id)])
                for ten in pro.tender_ids:
                    rec.item_ids=[(4,ten.item.id)]

    # @api.onchange('item')
    # def onchange_method(self):
    #     ids = []
    #
    #     if self.project_id:
    #         pro = self.env['project.project'].search([('id', '=', self.project_id.id)])
    #         for rec in pro.tender_ids:
    #             ids.append(rec.item.id)
    #
    #     return {'domain': {'item': [('id', 'in', ids)]}}

    @api.onchange('product_id', 'item')
    def onchange_product_id(self):
        if self.product_id:
            self.name=self.product_id.name
            self.product_uom=self.product_id.uom_id.id




