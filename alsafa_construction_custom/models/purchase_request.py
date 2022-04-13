from odoo import fields, models, api

from odoo.exceptions import ValidationError
class Purchase(models.Model):
    _inherit = 'purchase.request.line'

    @api.constrains('product_id','product_qty')
    def _get_all_qty(self):
        for rec in self:
            if rec.request_id.project_id:

                planned_qty = sum(self.env['construction.material'].\
                    search([('job_id.project_id','=',rec.request_id.project_id.id),('product_id','=',rec.product_id.id)]).mapped('total_qty'))

                product_qty =sum(self.env['purchase.request.line'].\
                    search([('request_id.project_id','=',rec.request_id.project_id.id),('product_id','=',rec.product_id.id)]).mapped('product_qty'))
                print("====================",product_qty,planned_qty)
                # if product_qty>planned_qty:
                #
                #     raise ValidationError ("Product %s must be less  planned qty %s  you purchase quantity before %s"%(rec.product_id.name,planned_qty,product_qty))


class Purchase_orer_line (models.Model):
    _inherit = 'purchase.order.line'
    stock_qtv = fields.Float(related='product_id.qty_available',string='Quantity On Hand')


class PurchaseRequestLine (models.Model):
    _inherit = 'purchase.request.line'
    item_id = fields.Many2one('construction.tender', string='Item')

    @api.onchange('item_id')
    def change_item_id(self):
        items =[]
        for l in self.request_id.project_id.tender_ids:
            if l.type != 'main':
                items.append(l.id)
        return {'domain': {'item_id': [('id', 'in', items)]}}


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"



    # @api.model
    # def _prepare_item(self, line):
    #     res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_item(line)
    #     print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ", line)
    #     res.update({'item_id': self.line_id.item_id.id})
    #     print(res)
    #     return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        print( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXitemXXXXXXXXXXXXXXXX ", item)
        print( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXpoXXXXXXXXXXXX ", po)
        print( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXseXXXXXXXXXX ", self)
        res.update({'item_id': item.line_id.item_id.id})
        print(res)

        return res
