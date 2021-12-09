# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for pick in self.picking_ids:
            pick.incoterm_id = self.incoterm_id.id
        return res

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # def _prepare_picking(self):
    #     res = super(PurchaseOrderLine, self)._prepare_picking()
    #     print(">>>>>>>>>>>>>>>>>>>>Res<<<<<<<<<<<<<<<<<<<<<<", res)
    #     return res
