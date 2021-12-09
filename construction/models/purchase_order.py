from odoo import fields, models, api,_
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
class purchase_order(models.Model):
    _inherit = 'purchase.order'
    project_id= fields.Many2one(comodel_name='project.project', string='Project',)


    def _prepare_invoice(self):
        invoice =  super(purchase_order, self)._prepare_invoice()
        invoice['project_id'] = self.project_id.id
        return invoice


    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'project_id':self.project_id.id
        }



class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'
    project_id = fields.Many2one(comodel_name='project.project', string='Project', related="order_id.project_id",
                                 store=True)

    # job_cost_id = fields.Many2one('construction.job.cost', 'Job Cost')
    # item_ids = fields.Many2many('product.item', "item_id", "line_ids", string='Item', compute='_get_item_list')
    # item = fields.Many2one('product.item', string='Item', domain="[('id','in',item_ids)]")
    #
    # def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
    #
    #
    #     self.ensure_one()
    #     product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
    #     description_picking = product._get_description(self.order_id.picking_type_id)
    #     if self.product_description_variants:
    #         description_picking += self.product_description_variants
    #     date_planned = self.date_planned or self.order_id.date_planned
    #     return {
    #         # truncate to 2000 to avoid triggering index limit error
    #         # TODO: remove index in master?
    #         'name': (self.name or '')[:2000],
    #         'product_id': self.product_id.id,
    #         'date': date_planned,
    #         'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
    #         'location_id': self.order_id.partner_id.property_stock_supplier.id,
    #         'location_dest_id': (self.orderpoint_id and not (
    #                     self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
    #         'picking_id': picking.id,
    #         'partner_id': self.order_id.dest_address_id.id,
    #         'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
    #         'state': 'draft',
    #         'purchase_line_id': self.id,
    #         'company_id': self.order_id.company_id.id,
    #         'price_unit': price_unit,
    #         'picking_type_id': self.order_id.picking_type_id.id,
    #         'group_id': self.order_id.group_id.id,
    #         'origin': self.order_id.name,
    #         'description_picking': description_picking,
    #         'propagate_cancel': self.propagate_cancel,
    #         'route_ids': self.order_id.picking_type_id.warehouse_id and [
    #             (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
    #         'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
    #         'product_uom_qty': product_uom_qty,
    #         'product_uom': product_uom.id,
    #         'item':self.item.id if self.item else ''
    #     }
    # @api.depends('project_id')
    # def _get_item_list(self):
    #     ids = []
    #     for rec in self:
    #         rec.item_ids = []
    #         if rec.project_id:
    #             pro = self.env['project.project'].search([('id', '=', rec.project_id.id)])
    #             for ten in pro.tender_ids:
    #                 rec.item_ids = [(4, ten.item.id)]