from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
class Bank (models.Model):
    _inherit = 'res.bank'
    journal_collection = fields.Many2one('account.journal', string=" Collection Journal",
                                         domain=[('cheque_collection', '=', True)])
class Journal (models.Model):
    _inherit = 'account.journal'
    cheque_recieve = fields.Boolean("Recieve Cheque",default=False)

    cheque_under_collection = fields.Boolean("Cheque Under Collection",default=False)
    cheque_collection = fields.Boolean("Cheque Collection",default=False)
    cheque_rejected = fields.Boolean("Cheque Rejected",default=False)
    cheque_return = fields.Boolean("Cheque Return",default=False)
    cheque_close = fields.Boolean("Cheque Close",default=False)
    cheque_send = fields.Boolean("Send Cheque", default=False)
    cheque_cancel= fields.Boolean("Cancel Cheque", default=False)
    cheque_cash= fields.Boolean("Cash Cheque", default=False)
    cheque_vendor = fields.Boolean("Vendor Cheque", default=False)
    transfer = fields.Boolean("Transfer Cheque", default=False)
    collection_journal = fields.Many2one("account.journal")