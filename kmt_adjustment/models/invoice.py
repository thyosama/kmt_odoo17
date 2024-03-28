# -*- coding: utf-8 -*-

from odoo import fields, models, api

class Prtner(models.Model):
    _inherit = "res.partner"
    vendor_code = fields.Char(string="Vendor Code")

class AccountMove(models.Model):
    _inherit = "account.move"

    ra_invoice_no = fields.Char('RA Invoice Number')
    client_po_number = fields.Char('Client P.O Number ')
    vendor_code = fields.Char(string="Vendor Code", related='partner_id.vendor_code',store=True)

