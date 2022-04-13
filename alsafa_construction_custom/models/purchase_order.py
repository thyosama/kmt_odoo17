from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    item_id = fields.Many2one('construction.tender', string='Item')
    project_id = fields.Many2one('project.project', string='Project')

    @api.onchange('item_id', 'product_id')
    def change_item_id(self):
        items =[]
        for l in self.order_id.project_id.tender_ids:
            if l.type != 'main':
                items.append(l.id)
        return {'domain': {'item_id': [('id', 'in', items)]}}


class Purchase(models.Model):
    _inherit = 'purchase.order'
    state = fields.Selection(selection_add=[('second_approval', 'Second Approval'),])


    # def button_approve(self, force=False):
    #     self.write({'state': 'second_approval'})
    #
    #     return {}
    #
    #
    #
    def button_approve_2(self):
        self.state = 'second_approval'

    # def button_approve_2(self):
    #     self.button_confirm()
    #     self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
    #     self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
    #     return {}

