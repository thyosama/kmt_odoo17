from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from num2words import num2words

class wizard(models.Model):
    _name = 'account.payment.wizard'
    journal_under_collection = fields.Many2one('account.journal', string="Under Collection Journal",
                                               domain=[('cheque_under_collection', '=', True)])
    journal_collection = fields.Many2one('account.journal', string=" Collection Journal",
                                         domain=[('cheque_collection', '=', True)])
    date_under_collection = fields.Date("Under Collection Date ")
    date_collection = fields.Date("Collection Date ")
    state_cheque2 = fields.Selection([('draft', 'Draft'), ('posted', 'Received'), ('under_collect', 'Under collection'),
                                      ('sent', 'Sent'), ('reconciled', 'Collect'), ('cancelled', 'Reject'),
                                      ('return', 'Returned'),
                                      ('close', 'Closed'), ('payment_vendor', 'Payment Vendor')],
                                     default='draft', copy=False)
    payment_id  = fields.Many2many("account.payment","p_id","id")
    is_transfer = fields.Boolean()
    is_pay_cash = fields.Boolean()
    journal_transfer = fields.Many2one('account.journal', string="Transfer Journal", domain=[('transfer', '=', True)])
    transfer_date = fields.Date("Transfer Date ")
    journal_cash = fields.Many2one('account.journal', string="Transfer Journal", domain=[('cheque_cash', '=', True)])
    date_cash = fields.Date("Transfer Date ")
    def save_payment_multi(self):

        for rec in self.payment_id:

            if rec.state_cheque in ('posted','cancelled') and self.is_pay_cash==True \
                    and rec.cheque_ref_amount<rec.amount :
                rec.payment_cach()
                payment_method = self.env['account.payment.method'].search(
                    [('code', '=', 'check'), ('payment_type', '=', 'inbound')], limit=1)
                payment_id = self.env['account.payment'].create({
                    'partner_type':rec.partner_type,
                    'payment_type':rec.payment_type,
                    'partner_id':rec.partner_id.id,
                    'payment_method_id':payment_method.id or '',
                    'cheque_ref_id': rec.id,
                    'communication': rec.cheque_bank.name + "/" + rec.cheque_no,
                    'amount':rec.amount,
                    'journal_id':self.journal_cash.id,
                    'payment_date':self.date_cash


                })

                # 'default_communication': self.cheque_bank.name + "/" + self.cheque_no
            if rec.state_cheque=='posted' and self.is_transfer==True:

                rec.journal_transfer=self.journal_transfer
                rec.transfer_date=self.transfer_date
                rec.transfer_journal_check()
                rec.is_transfer = False

            if self.state_cheque2 == 'under_collect' and rec.state_cheque=='posted':
                rec.journal_under_collection=self.journal_under_collection.id
                rec.date_under_collection=self.date_under_collection
                rec.get_under_collection_journal()

            elif self.state_cheque2 == 'reconciled' and rec.state_cheque=='under_collect':
                rec.date_collection = self.date_collection
                rec.journal_collection = self.journal_collection.id
                if rec.type_cheq == 'recieve_chq':

                    rec.get_collect_form_bank()
                # if rec.type_cheq == 'send_che':
                #     rec.get_collect_form_bank_send_cheque()

