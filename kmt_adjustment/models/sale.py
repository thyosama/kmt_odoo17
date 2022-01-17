# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_po_number = fields.Char('Client P.O Number ')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['client_po_number'] = self.client_po_number
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    product_availability = fields.Selection(
        string='Product Availability',
        selection=[('1', 'Stock'),
                   ('2', 'Not Stock')], compute='compute_product_availability')

    @api.depends('name', 'product_id', 'product_uom_qty')
    def compute_product_availability(self):
        for rec in self:
            rec.product_availability = '2'
            qunat_ids = self.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.warehouse_id.lot_stock_id.id),
                ('location_id.usage', 'in', ['internal', 'transit'])
            ])
            x_quantity = sum(line.quantity for line in qunat_ids)
            if x_quantity - rec.product_uom_qty>0:
                rec.product_availability = '1'
