from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_middle_account = fields.Many2one('account.account', string="Middle account Recieve ")
    ks_middle_account_send = fields.Many2one('account.account', string="Middle account send")
    ks_payment_cash = fields.Boolean(string="Payment Cash")
    ks_payment_vendor = fields.Boolean(string="Payment Vendor")
    ks_payment_return_cash = fields.Boolean(string="Return Cheque if pay cash")
    middle_account = fields.Boolean("Middle Account")
    ks_payment_return_cash_send = fields.Boolean(string="Return Cheque if pay cash Send")
    x_ks_payment_cash_send = fields.Boolean(string="Payment Cash Send")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_middle_account = fields.Many2one('account.account', string="Middle account Recieved",
                                        related='company_id.ks_middle_account', readonly=False)
    ks_middle_account_send = fields.Many2one('account.account', string="Middle account Send",
                                             related='company_id.ks_middle_account_send', readonly=False)
    ks_payment_cash = fields.Boolean(related='company_id.ks_payment_cash', readonly=False, string="Payment Cash")
    ks_payment_vendor = fields.Boolean(related='company_id.ks_payment_vendor', readonly=False, string="Payment Vendor")
    ks_payment_return_cash = fields.Boolean(related='company_id.ks_payment_return_cash', readonly=False,
                                            string="Return Cheque if pay cash")
    middle_account = fields.Boolean(string="Middle Account", related='company_id.middle_account', readonly=False)
    ks_payment_return_cash_send = fields.Boolean(string="Return Cheque if pay cash Send",related='company_id.ks_payment_return_cash_send', readonly=False)
    ks_payment_cash_send = fields.Boolean(string="Payment Cash Send",related='company_id.x_ks_payment_cash_send', readonly=False)