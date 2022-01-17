# -*- coding: utf-8 -*-

from odoo import fields, models,api,_
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('default_code')
    def constrains_product_default_code(self):
        for rec in self:
            product_id = self.env['product.template'].search([
                ('default_code', '=', rec.default_code),
                ('default_code', '!=', False),
                ('id', '!=', rec.id),
            ],limit=1)
            if product_id:
                raise ValidationError(_('This Internal Reference already exist in other product [%s]')%product_id.name)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains('default_code')
    def constrains_template_default_code(self):
        for rec in self:
            product_id = self.env['product.product'].search([
                ('default_code', '=', rec.default_code),
                ('default_code', '!=', False),
                ('id', '!=', rec.id),
            ], limit=1)
            if product_id:
                raise ValidationError(_('This Internal Reference already exist in other product [%s]')%product_id.name)

