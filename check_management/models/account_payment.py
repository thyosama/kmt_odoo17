from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from num2words import num2words
import calendar
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')

# default_account_id





class AccountMove(models.Model):
    _inherit = 'account.move'
    cheque_number = fields.Char(string="Cheque Number")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = 'id'
    cheque_number = fields.Char(related='move_id.cheque_number', string="Cheque Number")


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    journal_id = fields.Many2one("account.journal", string="Journal", domain=[('cheque_cash', '=', True)],copy=False)
    journal_cheque = fields.Many2one('account.journal', string="Journal", copy=False)
    journal_under_collection = fields.Many2one('account.journal', string="Under Collection Journal",
                                               domain=[('cheque_under_collection', '=', True)],copy=False)
    journal_collection = fields.Many2one('account.journal', string=" Collection Journal",
                                         domain=[('cheque_collection', '=', True)],copy=False)
    journal_reject = fields.Many2one('account.journal', string="Rejected Journal",
                                     domain=[('cheque_rejected', '=', True)],copy=False)

    journal_return = fields.Many2one('account.journal', string="Return Journal",copy=False, domain=[('cheque_return', '=', True)])
    journal_close = fields.Many2one('account.journal', string="Close Journal", copy=False,domain=[('cheque_close', '=', True)])
    journal_cancel = fields.Many2one('account.journal', string="Cancel Journal",copy=False, domain=[('cheque_cancel', '=', True)])
    journal_last = fields.Many2one('account.journal', string="Current Journal", compute='_get_last_journal', store=True)
    journal_vendor = fields.Many2one('account.journal', string="Vendor Journal", copy=False,domain=[('cheque_vendor', '=', True)])
    date_under_collection = fields.Date("Under Collection Date ",copy=False)
    date_collection = fields.Date("Collection Date ",copy=False)
    date_rejected = fields.Date("Rejected Date",copy=False)
    date_return = fields.Date("Returned Date",copy=False)
    date_close = fields.Date("Close Date",copy=False)
    date_cancel = fields.Date("Cancel Date",copy=False)
    date_vendor = fields.Date("Payment Date",copy=False)
    effective_date = fields.Date("Due Date",copy=False)
    cheque_no = fields.Char("Cheque Number", copy=False)
    type_cheq = fields.Selection([('send_che', 'Send Cheque'), ('recieve_chq', 'Recieve Cheque')], string="Type")
    state_cheque = fields.Selection([('draft', 'Draft'), ('posted', 'Received'), ('under_collect', 'Under collection'),
                                     ('sent', 'Sent'), ('reconciled', 'Collect'), ('cancelled', 'Reject'),
                                     ('return', 'Returned'), ('close', 'Closed'),('payment_vendor','Vendor Payment')],
                                    default='draft', copy=False)
    state_cheque2 = fields.Selection([('draft', 'Draft'), ('posted', 'Received'), ('under_collect', 'Under collection'),
                                      ('sent', 'Sent'), ('reconciled', 'Collect'), ('cancelled', 'Reject'),
                                      ('return', 'Returned'), ('close', 'Closed'),('payment_vendor','Vendor Payment')],
                                     default='draft', copy=False)

    is_cheque = fields.Boolean(default=False, copy=False)
    is_cash = fields.Boolean(default=False, copy=False)
    cheque_bank = fields.Many2one("res.bank", string="Cheque Bank")
    employee_name = fields.Many2one("hr.employee", string="Employee Name")
    # journal_cheq = fields.Many2one("account.journal" ,string="Journal")
    check_mid = fields.Boolean("Middle account",copy=False)
    middle_account_company_id = fields.Boolean(related="company_id.middle_account")
    account_med = fields.Many2one("account.account", string="Intermediate account ",
                                  related='company_id.ks_middle_account')
    account_med_send = fields.Many2one("account.account", string="Intermediate account ",
                                       related='company_id.ks_middle_account_send')
    document_id = fields.Many2one(comodel_name="cheque.document", string="دفتر شيكات", copy=False)
    cheque_id = fields.Many2one(comodel_name="account.cheque", string="شيك",copy=False )

    cheque_ref_id = fields.Many2one(comodel_name="account.payment", string="شيك", copy=False)
    cheque_payment_id = fields.Many2one(comodel_name="account.payment", string="Cheque Number",copy=False )
    cheque_ref_amount = fields.Float(string="amount", copy=False)
    payment_done = fields.Boolean(compute='_get_payment_amount', copy=False, default=False)
    delegate = fields.Char('Delegate')
    total_in_words = fields.Char(compute="_total_in_words")
    hide_payment_method = fields.Boolean(compute="_compute_hide_payment_method")
    vendor_id = fields.Many2one("res.partner", string="Vendor",copy=False)
    ks_payment_cash = fields.Boolean(related='company_id.ks_payment_cash', string="Payment Cash")
    ks_payment_cash_send = fields.Boolean(related='company_id.x_ks_payment_cash_send', string="Payment Cash")
    ks_payment_vendor = fields.Boolean(related='company_id.ks_payment_vendor', string="Payment Vendor")
    is_transfer = fields.Boolean(default=False)
    journal_transfer = fields.Many2one('account.journal', string="Transfer Journal", domain=[('transfer', '=', True)])
    transfer_date = fields.Date("Transfer Date ",copy=False)
    ks_payment_return_cash = fields.Boolean(related='company_id.ks_payment_return_cash',
                                            string="Return Cheque if pay cash")
    is_return_to_customer = fields.Boolean(default=False, copy=False)







    def get_currancy(self):
        if self.company_id.currency_id:
            return self.company_id.currency_id.id
        else:
            return []
    currency_id = fields.Many2one("res.currency",default=lambda self: self.env.company.currency_id)

    @api.onchange("cheque_bank")
    def get_cheque_bank_journal(self):
        if self.cheque_bank :
            if self.cheque_bank.journal_collection:
                self.journal_collection = self.cheque_bank.journal_collection.id
    @api.depends('name')
    def _compute_hide_payment_method(self):
        for rec in self:
            if self.env.user.has_group("check_management.group_payment_method"):
                rec.hide_payment_method = False
            else:
                rec.hide_payment_method = True

    @api.depends('amount')
    def _total_in_words(self):
        for rec in self:
            if rec.amount:
                rec.total_in_words = num2words(rec.amount, lang='ar')

    def _get_payment_amount(self):
        for rec in self:
            if rec.cheque_ref_amount >= rec.amount:
                rec.payment_done = True
            else:
                rec.payment_done = False

    @api.onchange('document_id')
    def _get_journal_document(self):
        if self.document_id:
            self.cheque_bank = self.document_id.bank_name.id
        if self.document_id.account_id:
            self.journal_collection = self.env['account.journal'].search(
                ['|', ('default_account_id', '=', self.document_id.account_id.id)
                    , ('default_account_id', '=', self.document_id.account_id.id)]).id or ''
        if self.document_id.journal_id:
            self.journal_collection = self.document_id.journal_id.id

        if self.document_id:
            cheques_dcument = self.env['account.cheque'].search([('document_id', '=', self.document_id.id), \
                                                                 ('name', '=', self.cheque_no)])
            ids=[]
            for rec in self.document_id.cheques_ids:
                find_check = self.env['account.payment'].search([('cheque_no','=',rec.name)])
                if not find_check:
                    ids.append(rec.id)

            domain = {'cheque_id': [('document_id','=',self.document_id.id),('id','in',ids)]}
            return {'domain': domain}


    @api.onchange('cheque_id', 'document_id')
    def set_cheque_no(self):
        if self.document_id and self.document_id.gap == False:
            for rec in self.document_id.cheques_ids:
                cheques = self.env['account.payment'].search([('cheque_no', '=', rec.name)], limit=1)
                if not cheques and not self.cheque_id:
                    self.cheque_id = rec.id
                    break
        # if self.document_id.gap == True and self.cheque_id:
        #     for rec in self.document_id.cheques_ids:
        #         cheques = self.env['account.payment'].search([('cheque_no', '=', rec.name)], limit=1)
        #         if not cheques and self.cheque_id.id > rec.id:
        #             raise ValidationError("Please must be choose cheque Number %s first" % (rec.name))

        if self.cheque_id:
            self.cheque_no = self.cheque_id.name

    @api.model
    def fields_get(self, fields=None):

        hide = ['is_transfer', 'transfer_date', 'journal_transfer', 'ks_payment_cash', 'ks_payment_vendor',
                'cheque_ref_amount', 'journal_cheque', 'date_under_collection', 'cheque_ref_id','date_collection',
                'date_rejected', 'journal_vendor', 'date_vendor', 'state_cheque2', 'date_return', 'date_close',
                'journal_reject', 'journal_under_collection', 'journal_collection', 'journal_return', 'journal_close']

        res = super(AccountPayment, self).fields_get()

        for field in hide:
            res[field]['selectable'] = False

        return res

    # def get_first_id(self):
    #     payment_method = self.env['account.payment.method'].search([('code', '=', 'check')
    #                                                                    , ('payment_type', '=', 'inbound')])
    #     if not payment_method:
    #         payment_method = self.env['account.payment.method'].create(
    #             {'code': 'check', 'name': 'Checks', 'payment_type': 'inbound'})
    #     return self.env['account.payment.method'].search([], limit=1).id


    _sql_constraints = [
        ('cheque_no', 'UNIQUE (cheque_no)', 'Cheque Number must be unique')
    ]
    # @api.onchange('journal_cheque')
    # def onchnage_journal_cheque(self):
    #     if self.journal_cheque:
    #         self.journal_id=self.journal_cheque.id

    @api.depends('state_cheque')
    def _get_last_journal(self):

        for rec in self:

            if rec.state_cheque == 'posted' or rec.state_cheque == 'draft' or rec.state_cheque == 'sent':
                rec.journal_last = rec.journal_id.id
            elif rec.state_cheque == 'under_collect':
                rec.journal_last = rec.journal_under_collection.id
            elif rec.state_cheque == 'reconciled':
                rec.journal_last = rec.journal_collection.id
            elif rec.state_cheque == 'return':
                rec.journal_last = rec.journal_return.id
            elif rec.state_cheque == 'cancelled':
                rec.journal_last = rec.journal_reject.id
            elif rec.state_cheque == 'close':
                rec.journal_last = rec.journal_close.id
            elif rec.state_cheque == 'payment_vendor':
                rec.journal_last = rec.journal_vendor.id
            if not rec.journal_last:
                rec.journal_last=rec.journal_cheque.id

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0.0:
            raise ValidationError("This payment amount should be greater than 0.0")

    def action_post(self):
        self.state_cheque = 'posted'
        return super(AccountPayment, self).action_post()

    @api.constrains('payment_method_line_id')
    def _check_payment_method_line_id(self):
        ''' Ensure the 'payment_method_line_id' field is not null.
        Can't be done using the regular 'required=True' because the field is a computed editable stored one.
        '''
        for pay in self:
            if not pay.payment_method_line_id and  pay.is_cheque==False:
                raise ValidationError(_("Please define a payment method line on your payment."))
    def return_cheque_cash(self):# return cheque to customer at pay is cah
        lines = []
        if self.type_cheq=='send_che':
            if self.account_med and self.check_mid == True:
                property_account = self.account_med_send
                second_journal_line = {
                    'account_id': self.account_med_send.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'credit': self.amount,
                    'debit': 0,
                }
            else:
                property_account = self.partner_id.property_account_payable_id
                second_journal_line = {
                    'account_id': self.partner_id.property_account_payable_id.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'credit': self.amount,
                    'debit': 0,
                }

            property_account_journal = self.journal_cheque.default_account_id
            first = {
                'account_id': self.journal_cheque.default_account_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,

                'date_maturity': self.effective_date,
                'credit': 0,
                'debit': self.amount,
            }

            lines.append((0, 0, second_journal_line))
            lines.append((0, 0, first))


        elif self.type_cheq=='recieve_chq':

            if self.account_med and self.check_mid == True:
                property_account = self.account_med
                second_journal_line = {
                    'account_id': self.account_med.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'debit': self.amount,
                    'credit': 0,
                }
            else:
                property_account = self.partner_id.property_account_receivable_id
                second_journal_line = {
                    'account_id': self.partner_id.property_account_receivable_id.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'debit': self.amount,
                    'credit': 0,
                }

            if self.journal_reject:
                property_account_journal = self.journal_reject.default_account_id
                first = {
                    'account_id': self.journal_reject.default_account_id.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'debit': 0,
                    'credit': self.amount,
                }
            else:
                property_account_journal = self.journal_id.default_account_id
                first = {
                    'account_id': self.journal_id.default_account_id.id,
                    'partner_id': self.partner_id.id,
                    'name': self.ref,
                    'date_maturity': self.effective_date,
                    'debit': 0,
                    'credit': self.amount,
                }

            lines.append((0, 0, second_journal_line))
            lines.append((0, 0, first))
            move2 = self.env['account.move'].create({'date': datetime.today(),
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_id.id if not self.journal_reject else self.journal_reject.id,
                                                     'line_ids': lines,
                                                     'cheque_number': self.cheque_no,

                                                     })
            # self.state_cheque = 'return'
        move2 = self.env['account.move'].create({'date': datetime.today(),
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',

                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_id.id if not self.journal_reject else self.journal_reject.id,
                                                 'line_ids': lines,
                                                 'cheque_number': self.cheque_no,

                                                 })

        move2.post()
        self._get_reconsile(property_account)
        self._get_reconsile(property_account_journal)
    def write(self,vals):
        res = super(AccountPayment, self).write(vals)
        if 'journal_cheque' in vals:
            for rec in self:
                rec.journal_last=rec.journal_cheque
                rec.move_id.journal_id=rec.journal_cheque
        for rec in self:
            if rec.cheque_no:
                rec.move_id.cheque_number = rec.cheque_no
            #self.move_id.ref=self.cheque_no

            for rec in self.move_id.line_ids:
                rec.name = self.ref
                # rec.ref = self.cheque_no


        return res
    @api.model
    def create(self, vals):
        if vals.get('journal_cheque'):
            vals['journal_id'] = vals['journal_cheque']
            #self._compute_payment_method_line_id()
            # payment_method = self.env['account.payment.method'].search([('code', '=', 'check')])
            # payment_method_line_id = self.env['account.payment.method.line']\
            #     .search([('payment_method_id','=',payment_method.id)],limit=1)
            # if not payment_method:
            #     payment_method = self.env['account.payment.method'].create(
            #         {'code': 'check', 'name': 'check', 'payment_type': 'outbound'})
            #     payment_method_line_id = self.env['account.payment.method.line'].create({
            #         'payment_method_id':payment_method.id,
            #         'name':"Cheques"
            #
            #     })

            # vals['payment_method_line_id'] = payment_method_line_id.id
        if 'cheque_ref_id' in vals:
            if vals['cheque_ref_id'] != False:
                payments = self.env['account.payment'].search([('cheque_ref_id', '=', vals['cheque_ref_id'])])
                current_payments = self.env['account.payment'].search([('id', '=', vals['cheque_ref_id'])], limit=1)
                total_amount = vals['amount']
                if len(payments) == 0 and current_payments.company_id.ks_payment_return_cash == True:

                    current_payments.return_cheque_cash()
                    current_payments.is_return_to_customer = True
                for rec in payments:
                    total_amount += rec.amount
                current_payments.cheque_ref_amount = total_amount

                if total_amount == current_payments.amount:
                    current_payments.state_cheque = 'reconciled'
                elif total_amount > current_payments.amount:
                    raise ValidationError("Payment Cash must be less than cheque")
        # if 'journal_cheque' in vals:
        #     vals['journal_id']=vals.get('journal_cheque')

        res = super(AccountPayment, self).create(vals)
        if res.is_cheque==True:
            res.name=res._get_payment_name(res.journal_cheque, res.date)
            res.journal_cheque=res.journal_id.id
        res.move_id.cheque_number= res.cheque_no
        print("===============11111111111111111111111111111111",res.move_id.name)
        return res


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
                :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
                    * amount:       The amount to be added to the counterpart amount.
                    * name:         The label to set on the line.
                    * account_id:   The account on which create the write-off.
                :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
                '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
                '%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
                '%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        balance=liquidity_balance
        if self.is_cheque ==False:
            self.name = ''

            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': liquidity_amount_currency,
                    'currency_id': currency_id,
                    'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                    'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.outstanding_account_id.id,
                },
                # Receivable / Payable.
                {
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                    'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                },
            ]
            if not self.currency_id.is_zero(write_off_amount_currency):
                # Write-off line.
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                    'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
        else:
            if self.account_med and self.check_mid == True:
                if self.type_cheq=='recieve_chq':
                    account_id = self.account_med
                if self.type_cheq=='send_che':
                    account_id = self.account_med_send
            elif self.type_cheq =='recieve_chq':
                account_id = self.partner_id.property_account_receivable_id
            else:
                account_id = self.partner_id.property_account_payable_id
            self.move_id.cheque_number= self.cheque_no

            if self.type_cheq =='recieve_chq':

                line_vals_list= self.create_journal_lines(
                    self.journal_cheque if self.journal_cheque
                    else self.journal_id,
                account_id)
            else:
                self.name=''
                line_vals_list = self.create_move_line_send_cheques( self.journal_cheque if self.journal_cheque
                    else self.journal_id,
                    account_id)



        return line_vals_list


    def _get_payment_name(self,journal,date):

        date_from="1-"+str(date.month)+"-"+str(date.year)
        date_to=str(calendar.monthrange(date.year, date.month)[1])+"-"+str(date.month)+"-"+str(date.year)
        sequ = self.env['account.move'].search([('journal_id','=',journal.id),('date','>=',datetime.strptime(date_from,"%d-%m-%Y")),('date','<=',datetime.strptime(date_to,"%d-%m-%Y"))])
        if not sequ:
            sequ=[1]
        if journal and date:
            name = journal.code+"/"+str(date.year)+"/"\
                   +str(date.month)+"/"+str(len(sequ)+1).zfill(5)

            if self.env['account.move'].search([('name','=',name)]):
                name = journal.code + "/" + str(date.year) + "/" \
                       + str(date.month) + "/" + str(len(sequ) + 2).zfill(5)

            return name
        else:
            return ''
    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields and pay.is_cheque ==False and pay.state_cheque=='draft':
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always contains:\n"
                        "- one journal item involving the outstanding payment/receipts account.\n"
                        "- one journal item involving a receivable/payable account.\n"
                        "- optional journal items, all sharing the same account.\n\n"
                    ) % move.display_name)

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, all the write-off journal items must share the same account."
                    ) % move.display_name)

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'payment_type': 'inbound' if liquidity_amount > 0.0 else 'outbound',
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })

                move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
                pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))
    def post_cheque(self):

        # if not self.journal_id.post_at_bank_rec:

        self.move_id.post()
        self.state_cheque = 'posted'
        self.state = 'posted'

        # self.get_employee_recieve()
        self.is_cheque = False


    def post_cheque_send(self):


        # if not self.journal_id.post_at_bank_rec:
        self.move_id.post()
        self.state_cheque = 'sent'
        self.state = 'posted'
        ch = ''
        # if self.state_cheque == 'sent':
        #     if len(str(self.id)) == 1:
        #         ch = '000' + str(self.id)
        #     elif len(str(self.id)) == 2:
        #         ch = '00' + str(self.id)
        #     elif len(str(self.id)) == 3:
        #         ch = '0' + str(self.id)
        #     else:
        #         ch = str(self.id)
        #     self.name = 'CUST.OUT' + "/" + str(datetime.now().year) + "/" + ch
        # self.get_employee_recieve()
        self.is_cheque = False


    def create_under_collection_journal(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'under_collect'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_state_cheque2': 'under_collect'}
        }
    def action_vendor_payment(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'payment_vendor'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_state_cheque2': 'payment_vendor'}
        }
    def collect_form_bank(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')

        self.state_cheque2 = 'reconciled'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'default_state_cheque2': 'reconciled'}, 'target': 'new'
        }

    def rejected_form_bank(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'cancelled'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'default_state_cheque2': 'cancelled'}, 'target': 'new'
        }

    def returned_to_customer(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'return'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'default_state_cheque2': 'return'}, 'target': 'new'
        }

    def cancel_send(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'cancelled'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'default_state_cheque2': 'cancelled'}, 'target': 'new'
        }

    def get_move_line(self):

        return {
            'name': _('Select Journal'),
            'view_mode': 'tree,form',

            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_order': 'id'},
            'domain': [('cheque_number', '=', self.cheque_no)]
        }

    def close_account_middle(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = 'close'
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'default_state_cheque2': 'close'}, 'target': 'new'
        }

    def create_move_line_send_cheques(self, journal, debit_account):
        lines = []

        second_journal_line = {
            'account_id': debit_account.id,
            'partner_id': self.partner_id.id,
             'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append(second_journal_line)
        first_journal_line = {
            'account_id': journal.default_account_id.id,
            'partner_id': self.partner_id.id,
             'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': 0,
            'credit': self.amount,
        }
        lines.append(first_journal_line)

        return lines
    def create_journal_send_state(self, journal, debit_account):
        lines = []

        second_journal_line = {
            'account_id': debit_account.id,
            'partner_id': self.partner_id.id,
             'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append((0, 0, second_journal_line))
        first_journal_line = {
            'account_id': journal.default_account_id.id,
            'partner_id': self.partner_id.id,
             'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': 0,
            'credit': self.amount,
        }
        lines.append((0, 0, first_journal_line))

        return lines

    def create_journal_lines(self, journal, credit_account):
        lines = []
        if self.is_cheque==False:
            self.name = self._get_payment_name(self.journal_id,self.date)
        else:
            self.name = ''




        if self.state_cheque == 'payment_vendor' and self.vendor_id:

            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.vendor_id.id,
                'name': self.ref,

                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        else:
            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.partner_id.id,
                 'name': self.ref,

                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        lines.append( second_journal_line)
        print("=================0",self.name)
        first_journal_line = {
            'account_id': journal.default_account_id.id,
            'partner_id': self.partner_id.id,
             'name': self.ref,

            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append(first_journal_line)

        return lines

    def create_journal_receive_state(self, journal, credit_account):
        lines = []

        if self.state_cheque == 'payment_vendor' and self.vendor_id:

            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.vendor_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        else:
            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        lines.append((0, 0, second_journal_line))
        first_journal_line = {
            'account_id': journal.default_account_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append((0, 0, first_journal_line))

        return lines
    def create_journal_payment_vendor(self, journal, credit_account):
        lines = []

        second_journal_line = {
            'account_id': credit_account.id,
            'partner_id': self.vendor_id.id,
            'name': self.ref,
            'date_maturity': self.effective_date,
            'credit': 0,
            'debit': self.amount,
        }
        lines.append((0, 0, second_journal_line))
        first_journal_line = {
            'account_id': journal.default_account_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'date_maturity': self.effective_date,
            'credit': self.amount,
            'debit': 0,
        }
        lines.append((0, 0, first_journal_line))

        return lines

    def _get_reconsile(self, credit_account):

        movee_line = self.env['account.move.line'].search(
            [('cheque_number', '=', self.cheque_no), ('account_id', '=', credit_account.id)])

        if len(movee_line) > 1:
            amls = []
            for rec in movee_line:
                if not rec.full_reconcile_id:
                    amls.append(rec.id)
            if amls:
                movee_line = self.env['account.move.line'].search(
                    [('id', 'in', amls)])

                self.env['account.full.reconcile'].create({

                    'reconciled_line_ids': [(6, 0, movee_line.ids)],
                })

    def get_under_collection_journal(self):
        move2 = []
        if self.state_cheque == 'posted':
            move2 = self.env['account.move'].create({'date': self.date_under_collection,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',
                                                      'name' :self._get_payment_name(self.journal_under_collection, self.date_under_collection),
                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_under_collection.id,
                                                     'line_ids': self.create_journal_receive_state(
                                                         self.journal_under_collection,
                                                         self.journal_id.default_account_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id':self.currency_id.id

                                                     })
            self.journal_collection = self.journal_under_collection.collection_journal.id if  self.journal_under_collection.collection_journal else False

            # if not self.journal_id.post_at_bank_rec:
            move2.post()
            self.state_cheque = 'under_collect'
            # self.get_employee_recieve()
            self._get_reconsile(self.journal_id.default_account_id)
        elif self.state_cheque == 'cancelled':

            move2 = self.env['account.move'].create({'date': self.date_under_collection,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_under_collection.id,
                                                     'name': self._get_payment_name(self.journal_under_collection,self.date_under_collection),
                                                     'line_ids': self.create_journal_receive_state(
                                                         self.journal_under_collection,
                                                         self.journal_reject.default_account_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

            # if not self.journal_id.post_at_bank_rec:
            move2.post()
            self.state_cheque = 'under_collect'
            # self.get_employee_recieve()
            self._get_reconsile(self.journal_reject.default_account_id)

        return move2
    def _get_payment_vendor(self):
        move2 = []
        if self.state_cheque == 'posted':
            move2 = self.env['account.move'].create({'date': self.date_vendor,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.vendor_id.id or '',

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_vendor.id,
                                                     'name': self._get_payment_name(self.journal_vendor,
                                                                                    self.date_vendor),

                                                     'line_ids': self.create_journal_payment_vendor(
                                                         self.journal_id, self.vendor_id.property_account_payable_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

            # if not self.journal_id.post_at_bank_rec:
            move2.post()
            self.state_cheque = 'payment_vendor'
            # self.get_employee_recieve()
            self._get_reconsile(self.journal_id.default_account_id)
        elif self.state_cheque == 'cancelled':

            move2 = self.env['account.move'].create({'date': self.date_under_collection,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',
                                                     'name': self._get_payment_name(self.journal_vendor,
                                                                                    self.date_vendor),

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_vendor.id,
                                                     'line_ids': self.create_journal_payment_vendor(

                                                         self.journal_reject,
                                                         self.vendor_id.property_account_payable_id, ),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

            # if not self.journal_id.post_at_bank_rec:
            move2.post()
            self.state_cheque = 'under_collect'
            # self.get_employee_recieve()
            self._get_reconsile(self.journal_reject.default_account_id)

        return move2

    def get_collect_form_bank(self):

        move2 = self.env['account.move'].create({'date': self.date_collection,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'name': self._get_payment_name(self.journal_collection,self.date_collection),
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_collection.id,
                                                 'line_ids': self.create_journal_receive_state(
                                                     self.journal_collection,
                                                     self.journal_under_collection.default_account_id),
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        move2.post()
        self.state_cheque = 'reconciled'
        # self.get_employee_recieve()
        self._get_reconsile(self.journal_under_collection.default_account_id)
        return move2

    def get_collect_form_bank_send_cheque(self):

        move2 = self.env['account.move'].create({'date': self.date_collection,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'name': self._get_payment_name(self.journal_collection,self.date_collection),
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_collection.id,
                                                 'line_ids': self.create_journal_send_state(
                                                     self.journal_collection,
                                                     self.journal_id.default_account_id),
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        move2.post()
        self.state_cheque2 = 'reconciled'
        # self.get_employee_recieve()
        self._get_reconsile(self.journal_id.default_account_id)
        return move2

    def get_rejected_form_bank(self):
        account_id = ''
        if self.journal_under_collection.default_account_id:
            account_id = self.journal_under_collection.default_account_id
        elif self.state_cheque == 'posted':
            account_id = self.journal_id.default_account_id
        if self.state_cheque == "payment_vendor":
            move2 = self.env['account.move'].create({'date': self.date_rejected,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',
                                                     'name': self._get_payment_name(self.journal_reject,
                                                                                    self.date_rejected),

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_reject.id,
                                                     'line_ids': self.create_journal_receive_state(
                                                         self.journal_reject,
                                                         self.vendor_id.property_account_payable_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

            move2.post()
            self.state_cheque = 'cancelled'
            self._get_reconsile(self.vendor_id.property_account_payable_id)
        else:

            move2 = self.env['account.move'].create({'date': self.date_rejected,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',
                                                     'name': self._get_payment_name(self.journal_reject,
                                                                                    self.date_rejected),

                                                     'company_id': self.company_id.id,
                                                     'journal_id': self.journal_reject.id,
                                                     'line_ids': self.create_journal_receive_state(
                                                         self.journal_reject,
                                                         account_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

        # if not self.journal_id.post_at_bank_rec:
            move2.post()
        self.state_cheque = 'cancelled'
        # self.get_employee_recieve()
        if not account_id:
            account_id=self.vendor_id.property_account_payable_id
        self._get_reconsile(account_id)
        return move2

    def get_returned_to_customer(self):
        lines = []
        property_account = ''
        if self.account_med and self.check_mid == True:
            property_account = self.account_med
            second_journal_line = {
                'account_id': self.account_med.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': self.amount,
                'credit': 0,
            }
        else:
            property_account = self.partner_id.property_account_receivable_id
            second_journal_line = {
                'account_id': self.partner_id.property_account_receivable_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': self.amount,
                'credit': 0,
            }
        lines.append((0, 0, second_journal_line))
        account_id = ''
        if self.state_cheque == 'posted':
            account_id = self.journal_id.default_account_id
        else:
            account_id = self.journal_reject.default_account_id

        first_journal_line = {
            'account_id': account_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'debit': 0,
            'date_maturity': self.effective_date,
            'credit': self.amount,
        }
        lines.append((0, 0, first_journal_line))
        print("lines", lines)
        move2 = self.env['account.move'].create({'date': self.date_return,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'name': self._get_payment_name(self.journal_return,self.date_return),
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_return.id,
                                                 'line_ids': lines,
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        print("lines", lines)
        move2.post()
        self._get_reconsile(account_id)
        self._get_reconsile(property_account)

        self.state_cheque = 'return'
        # self.get_employee_recieve()
        return move2

    def get_returned_to_customer_send(self):
        lines = []
        property_account = ''
        if self.account_med and self.check_mid == True:
            property_account = self.account_med_send
            second_journal_line = {
                'account_id': self.account_med_send.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        else:

            second_journal_line = {
                'account_id': self.partner_id.property_account_payable_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        first_journal_line = {
            'account_id': self.journal_id.default_account_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append((0, 0, first_journal_line))
        lines.append((0, 0, second_journal_line))
        account_id = ''

        move2 = self.env['account.move'].create({'date': self.date_cancel,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'name': self._get_payment_name(self.journal_cancel,self.date_cancel),
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_cancel.id,
                                                 'line_ids': lines,
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        move2.post()
        self._get_reconsile(self.journal_id.default_account_id)

        self.state_cheque = 'cancelled'
        # self.get_employee_recieve()
        return move2

    def get_close_to_customer(self):
        lines = []

        second_journal_line = {
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'debit': 0,
            'date_maturity': self.effective_date,
            'credit': self.amount,
        }

        first_journal_line = {
            'account_id': self.account_med.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'debit': self.amount,
            'credit': 0,
            'date_maturity': self.effective_date,
        }
        lines.append((0, 0, second_journal_line))
        lines.append((0, 0, first_journal_line))

        move2 = self.env['account.move'].create({'date': self.date_close,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_close.id,
                                                 'line_ids': lines,
                                                 'name': self._get_payment_name(self.journal_close,self.date_close),
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        move2.post()
        self.state_cheque = 'close'
        self._get_reconsile(self.account_med)
        # self.get_employee_recieve()
        return move2

    def get_close_to_customer_send(self):
        lines = []

        second_journal_line = {
            'account_id': self.partner_id.property_account_payable_id.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'debit': self.amount,
            'date_maturity': self.effective_date,
            'credit': 0,
        }
        lines.append((0, 0, second_journal_line))
        first_journal_line = {
            'account_id': self.account_med_send.id,
            'partner_id': self.partner_id.id,
            'name': self.ref,
            'debit': 0,
            'credit': self.amount,
            'date_maturity': self.effective_date,
        }
        lines.append((0, 0, first_journal_line))
        move2 = self.env['account.move'].create({'date': self.date_close,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_close.id,
                                                 'name': self._get_payment_name(self.journal_close,self.date_close),
                                                 'line_ids': lines,
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        move2.post()
        self.state_cheque = 'close'
        self._get_reconsile(self.account_med_send)
        # self.get_employee_recieve()
        return move2

    def save_payment(self):
        if self.is_transfer == True:
            self.transfer_journal_check()
            self.is_transfer = False

        if self.state_cheque2 == 'under_collect':
            self.get_under_collection_journal()
            self.state_cheque2 = 'under_collect'
        elif self.state_cheque2 == 'reconciled':
            if self.type_cheq == 'recieve_chq':
                self.get_collect_form_bank()
            if self.type_cheq == 'send_che':
                self.get_collect_form_bank_send_cheque()
            self.state_cheque = 'reconciled'

        elif self.state_cheque2 == 'cancelled':
            if self.type_cheq == 'send_che':
                self.get_returned_to_customer_send()
            if self.type_cheq == 'recieve_chq':
                self.get_rejected_form_bank()

            self.state_cheque = 'cancelled'
        elif self.state_cheque2 == 'return':
            if self.type_cheq == 'recieve_chq':
                self.get_returned_to_customer()

            self.state_cheque = 'return'


        elif self.state_cheque2 == 'close':
            if self.type_cheq == 'recieve_chq':
                self.get_close_to_customer()
            if self.type_cheq == 'send_che':
                self.get_close_to_customer_send()
            self.state_cheque = 'close'
        elif self.state_cheque2 == 'payment_vendor':
            self._get_payment_vendor()
            self.state_cheque = 'payment_vendor'
        self.state_cheque = self.state_cheque
        # return {'type': 'ir.actions.act_window_close'}

    def open_payment(self):
        return {
            'name': _('Payments'),
            'domain': [('id', '=', self.id)],
            'context': {'default_id': self.id},
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def payment_cach(self):
        self.is_cash = True

    def return_payment_cach(self):
        self.is_cash = False

    def create_payment_cash(self):
        view = self.env.ref('account.view_account_payment_form')
        payment_method = self.env['account.payment.method'].search(
            [('code', '=', 'check'), ('payment_type', '=', 'inbound')], limit=1)

        return {
            'name': _('Payment Cash'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'context': {'default_partner_type': self.partner_type,
                        'default_payment_type': self.payment_type,
                        'default_partner_id': self.partner_id.id,
                        'default_payment_method_id': payment_method.id or '',
                        'default_cheque_ref_id': self.id,
                        'default_cheque_payment_id': self.id,
                        'default_move_journal_types': ('bank', 'cash'),
                        'default_communication': self.cheque_bank.name if self.cheque_bank else '' + "/" + self.cheque_no},
            'target': 'new'
        }

    def get_payment_cheque(self):
        view = self.env.ref('account.view_account_payment_tree')
        view_form = self.env.ref('account.view_account_payment_form')

        return {
            'name': _('Payment'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            'res_model': 'account.payment',
            'context': {'default_partner_type': self.partner_type,
                        'default_payment_type': self.payment_type,
                        'default_partner_id': self.partner_id.id,
                        'default_cheque_ref_id': self.id,
                        'default_cheque_payment_id': self.id,
                        'default_move_journal_types': ('bank', 'cash'),
                        'default_communication': self.cheque_bank.name if self.cheque_bank else '' + "/" + self.cheque_no},
            'domain': [('cheque_ref_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    @api.onchange('amount')
    def get_sub_amount(self):
        if self.cheque_ref_id and self.amount:
            if self.amount > self.cheque_ref_id.amount:
                raise ValidationError("Payment Cash must be less than cheque")

    def return_send_cheque_cash(self):
        lines = []
        if self.is_return_to_customer==True:
            self.state_cheque = 'return'
            return True
        if self.account_med and self.check_mid == True:
            property_account = self.account_med
            second_journal_line = {
                'account_id': self.account_med.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': self.amount,
                'credit': 0,
            }
        else:
            property_account = self.partner_id.property_account_receivable_id
            second_journal_line = {
                'account_id': self.partner_id.property_account_receivable_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': self.amount,
                'credit': 0,
            }

        if self.journal_reject:
            property_account_journal = self.journal_reject.default_account_id
            first = {
                'account_id': self.journal_reject.default_account_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        else:
            property_account_journal = self.journal_id.default_account_id
            first = {
                'account_id': self.journal_id.default_account_id.id,
                'partner_id': self.partner_id.id,
                'name': self.ref,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }

        lines.append((0, 0, second_journal_line))
        lines.append((0, 0, first))
        move2 = self.env['account.move'].create({'date': datetime.today(),
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',

                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_id.id,
                                                 'name': self._get_payment_name(self.journal_id,datetime.today()),
                                                 'line_ids': lines,
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })
        self.state_cheque = 'return'
        move2.post()
        self._get_reconsile(property_account)
        self._get_reconsile(property_account_journal)

    # @api.onchange('amount', 'currency_id','journal_cheque')
    # def _onchange_amount(self):
    #     jrnl_filters = self._compute_journal_domain_and_types()
    #     journal_types = jrnl_filters['journal_types']
    #     domain_on_types = [('cheque_cash','=',True)]
    #     if self.invoice_ids:
    #         domain_on_types.append(('company_id', '=', self.invoice_ids[0].company_id.id))
    #     # if self.journal_id.type not in journal_types or (
    #     #         self.invoice_ids and self.journal_id.company_id != self.invoice_ids[0].company_id):
    #     #     self.journal_id = self.env['account.journal'].search(
    #     #         domain_on_types + [('company_id', '=', self.env.company.id)], limit=1)
    #     if self.journal_cheque:
    #         self.journal_id = self.journal_cheque.id
    #     if not self.journal_id:
    #         self.journal_id = self.env['account.journal'].search(
    #                 domain_on_types + [('company_id', '=', self.env.company.id)], limit=1)
    #     return {'domain': {'journal_id': jrnl_filters['domain'] + domain_on_types}}
    def transfer_journal(self):
        view = self.env.ref('check_management.view_account_payment_cheque_pop')
        self.state_cheque2 = ''
        self.is_transfer = True
        return {
            'name': _('Select Journal'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_is_transfer': True}
        }

    def transfer_journal_check(self):

        journal = self.get_journal_to_transfer()
        if journal:
            move2 = self.env['account.move'].create({'date': self.transfer_date,
                                                     'ref': "Cheque Num/" + self.cheque_no or '',
                                                     'partner_id': self.partner_id.id or '',

                                                     'company_id': self.company_id.id,
                                                     'name': self._get_payment_name(self.journal_transfer,
                                                                                    self.transfer_date),
                                                     'journal_id': self.journal_transfer.id,
                                                     'line_ids': self.create_journal_send_state(
                                                         journal,
                                                         self.journal_transfer.default_account_id),
                                                     'cheque_number': self.cheque_no,
                                                     'currency_id': self.currency_id.id

                                                     })

            # if not self.journal_id.post_at_bank_rec:
            move2.post()
            self.journal_last = self.journal_transfer.id
            self.state_cheque2 = self.state_cheque
            # self.get_employee_recieve()
            self._get_reconsile(journal.default_account_id)
            return move2

    def get_journal_to_transfer(self):
        for rec in self:
            if rec.state_cheque == 'posted' or rec.state_cheque == 'draft' or rec.state_cheque == 'sent':
                # rec.journal_last = rec.journal_id.id
                rec.journal_last = rec.journal_cheque.id
            elif rec.state_cheque == 'under_collect':
                rec.journal_last = rec.journal_under_collection.id
            elif rec.state_cheque == 'reconciled':
                rec.journal_last = rec.journal_collection.id
            elif rec.state_cheque == 'return':
                rec.journal_last = rec.journal_return.id
            elif rec.state_cheque == 'cancelled':
                rec.journal_last = rec.journal_reject.id
            elif rec.state_cheque == 'close':
                rec.journal_last = rec.journal_close.id
            elif rec.state_cheque == 'payment_vendor':
                rec.journal_last = rec.journal_vendor.id
            if not rec.journal_last:
                rec.journal_last = rec.journal_cheque.id

        return journal_last
    def unlink(self):
        if self.cheque_no and (self.state_cheque !='draft' or self.state=='posted'):
            raise ValidationError("You Cann't Delete Payment")
        res = super(AccountPayment, self).unlink()

        return res

    is_multi = fields.Boolean(default=False)

    def action_recieve_multi_cheque(self):
        for rec in self:
            if rec.state_cheque == 'draft':
                rec.post_cheque()

    def action_under_multi_cheque(self):
        ids = []
        print(">>>>>>>>>>>>>>>(((((((((((99999")

        return {
            'name': _('Under Collection '),
            'view_mode': 'form',
            'res_model': 'account.payment.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_state_cheque2': 'under_collect', 'default_payment_id': [(4, rec.id) for rec in self]}
        }

    def action_collect_multi_cheque(self):
        ids = []

        return {
            'name': _(' Collection '),
            'view_mode': 'form',
            'res_model': 'account.payment.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_state_cheque2': 'reconciled', 'default_payment_id': [(4, rec.id) for rec in self]}
        }

    # /// update 9/6/2021
    def action_transfer_multi_cheque(self):
        ids = []

        return {
            'name': _(' Transfer '),
            'view_mode': 'form',
            'res_model': 'account.payment.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_is_transfer': True, 'default_payment_id': [(4, rec.id) for rec in self]}
        }

    def action_pay_cash_multi_cheque(self):
        ids = []

        return {
            'name': _(' Pay Cash '),
            'view_mode': 'form',
            'res_model': 'account.payment.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_is_pay_cash': True, 'default_payment_id': [(4, rec.id) for rec in self]}
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                          submenu=submenu)
        action_id = self.env['ir.model.data'].search(['|', '|', ('name', '=', 'action_account_payments_payable'),
                                                      ('name', '=', 'action_account_payments'),
                                                      ('name', '=', 'action_payment_account_send')])

        ids = []

        for rec in action_id:
            ids.append(rec.res_id)

        if 'toolbar' in res:

            if 'params' in self.env.context:
                print("????????????????????", self.env.context['params']['action'])

                if self.env.context['params']['action'] in ids:
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>....1",ids)
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>....1",self.env.context['params']['action'])

                    for i in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][i]['name'] == "Recieve":
                            del res['toolbar']['action'][i]
                            break

                    for i in range(len(res['toolbar']['action'])):

                        if res['toolbar']['action'][i]['name'] == "UnderCollection":
                            del res['toolbar']['action'][i]
                            break
                    for i in range(len(res['toolbar']['action'])):

                        if res['toolbar']['action'][i]['name'] == "Collect":
                            del res['toolbar']['action'][i]
                            break
                    for i in range(len(res['toolbar']['action'])):

                        if res['toolbar']['action'][i]['name'] == "Transfer":
                            del res['toolbar']['action'][i]
                            break
                    for i in range(len(res['toolbar']['action'])):

                        if res['toolbar']['action'][i]['name'] == "Pay Cash":
                            del res['toolbar']['action'][i]
                            break

        return res

    ### SET DRAFT 20/6/2021
    def mass_editing(self):

        move_ids = self.env['account.move'].search([('cheque_number', '=', self.cheque_no)])
        if move_ids:
            for record in move_ids:
                record.button_draft()
                record.button_cancel()

        self.state_cheque = 'draft'
        self.state = 'draft'
        self.state_cheque2 = 'draft'


