# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    ra_invoice_no = fields.Char('RA Invoice Number')
    client_po_number = fields.Char('Client P.O Number ')

