# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Qauntity(models.Model):
    _inherit = 'quantity.survey.line'
    date = fields.Date(related='quantity_survey_id.date', store=True)


class MoveLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.constrains('quantity')
    def _get_quantity_qs(self):
        for rec in self:
            # if rec.invoice_id.type=='supconstractor':
            qs_lines = sum(self.env['quantity.survey.line'].search([
                ('state', '=', 'confirm'),
                ('tender_line', '=', rec.tender_id.id),
                ('project_id', '=', rec.project_id.id)
            ], order='id desc', limit=1).mapped('total_qty'))

            if qs_lines < rec.quantity:
                raise ValidationError('Total Quantity must be less than Quantity Survey')

            lines = sum(self.env['account.invoice.line'].search([
                ('invoice_id.state', '=', 'posted'),
                ('tender_id', '=', rec.tender_id.id),
                ('project_id', '=', rec.project_id.id)
            ]).mapped('current_qty'))
            if lines > qs_lines:
                raise ValidationError('Total Quantity must be less than Quantity Survey')
