# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    unit_price_readonly = fields.Boolean(compute='_get_unit_price_readonly')

    @api.depends('company_id')
    def _get_unit_price_readonly(self):
        for rec in self:
            if self.env.user.has_group('sale_order_access.group_unit_price_readonly'):
                rec.unit_price_readonly = True
            else:
                rec.unit_price_readonly = False



class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        arch = etree.XML(res['arch'])
        if self._name == 'sale.order':
            if self.env.user.has_group('sale_order_access.group_sale_order_readonly'):
                elements = arch.xpath(f"//{view_type}")
                for element in elements:
                    element.set('create', '0')
                    element.set('edit', '0')
                    element.set('delete', '0')
                    element.set('duplicate', '0')
                if view_type == 'form':
                    header_elements = arch.xpath("//header")
                    if header_elements:
                        for header_elem in header_elements:
                            header_elem.set('invisible','1')
                    chatter_elements = arch.xpath("//div[@class='oe_chatter']")
                    if chatter_elements:
                        for chatter_elem in chatter_elements:
                            chatter_elem.set('invisible','1')
                    sm_elements = arch.xpath("//div[@name='button_box']")
                    if sm_elements:
                        for sm_elem in sm_elements:
                            sm_elem.set('invisible','1')
                if view_type == 'tree':
                    header_elems = arch.xpath("//button")
                    if header_elems:
                        for header_elem in header_elems:
                            header_elem.set('invisible','1')
                    # server_actions = self.env['ir.actions.server'].search([('model_id.model','=','sale.order')])
                    # if server_actions:
                    #     for server in server_actions:
                    #         print('server',server.name)
                    #         server.binding_model_id = False
                    # actions = self.env['ir.actions.act_window'].search([('binding_model_id.model','=','sale.order'),('target','=','new')])
                    # if actions:
                    #     for action in actions:
                    #         print('action',action.name)
                    #         action.binding_model_id = False
        res['arch'] = etree.tostring(arch)
        return res
