from datetime import datetime

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from json import dumps
import json




class AccountMove(models.Model):
    _inherit = 'account.move'
    invoice_id = fields.Many2one('account.invoice', string="Invoice")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    type_invoice = fields.Selection(related='move_id.invoice_id.type',store=True,index=True)


class Invoice(models.Model):
    _name = 'account.invoice'
    name = fields.Char(compute="_get_invoice_name",string="Name")
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    type_move = fields.Selection([('process', 'Process'), ('final', 'Final')], string="Type")
    contract_id = fields.Many2one("construction.contract", string="Contract")
    contract_value = fields.Float(related='contract_id.total_value',store=True,index=True)
    contract_date = fields.Date(related='contract_id.date', string="Contract Date", store=True, index=True)
    contract_date = fields.Date(related='contract_id.date', string="Contract Date", store=True, index=True)
    number_manual = fields.Char("Manual number")
    project_id = fields.Many2one(related='contract_id.project_id', string="Project",store=True,index=True)
    partner_id = fields.Many2one(related="project_id.partner_id", string="Customer", store=True, index=True)
    sub_contactor = fields.Many2one(related='contract_id.sub_contactor', string="sub contractor Name")
    deduction_ids = fields.One2many("contract.deduction.lines.invoice", "invoice_id",
                                    string="Deductions", domain=[('type', '=', 'deduction')])
    allowance_ids = fields.One2many("contract.addition.lines.invoice", "invoice_id",
                                    string="Additions", domain=[('type', '=', 'addition')])
    is_tender = fields.Boolean(default=False)
    invoice_line = fields.One2many('account.invoice.line', 'invoice_id', string="Lines")
    date = fields.Date(string="Date", default=datetime.today())

    due_date = fields.Date(string="Due Date", default=datetime.today())

    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string="State", default='draft')
    total_value = fields.Float("Total Value", compute='_calculate_total_value')
    last_total_value = fields.Float("Total Previous Value", compute='_calculate_total_value')
    current_total_value = fields.Float("Total Current Value", compute='_calculate_total_value',store=True,index=True)
    current_total_value_deduction = fields.Float("current deduction", compute='_calculate_total_deduction_addition',store=True,index=True)
    current_total_value_addition = fields.Float("Current Additional", compute='_calculate_total_deduction_addition',store=True,index=True)
    payment_amount = fields.Float("payment Amount", compute="compute_payment_amount")
    payment_count = fields.Integer("payment Count", compute='compute_payment_count')
    payment_state = fields.Selection([('not_paid', 'Not paid'), ('in_payment', 'Partially Paid'), ('paid', 'Paid')]
                                     , compute='_get_payment_state',store=True,index=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    amount_price_total = fields.Float(compute='_get_amount_price_total',store=True,index=True)
    remaining_value = fields.Float("remaining Value",compute='get_remaining')
    is_last = fields.Boolean(compute='_get_last_invoice')
    payment_ids_line = fields.Many2many("account.payment","p_id","invoice_id",string="Payment",compute='get_payment_ids')
    is_payment_visible = fields.Boolean(compute='get_payment_ids')

    def register_payment(self):
        view_form = self.env.ref('construction.invoice_payment_view_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'construction.payment.wizard',
            'target': 'new',
            'domain': [('invoice_id', '=', self.id)],
            'context': {
                'default_invoice_id': self.id,
                'default_partner_id': self.sub_contactor.id,
                'default_contract_id': self.contract_id.id,
                'default_project_id': self.project_id.id,
            }
        }

    @api.depends('payment_ids_line')
    def compute_payment_amount(self):
        for rec in self:
            payment_ids = self.env['account.payment'].search([('invoice_ids', '=', rec.id)])
            print()
            rec.payment_amount = sum(l.amount for l in payment_ids)

    @api.depends('payment_ids_line')
    def compute_payment_count(self):
        for rec in self:
            payment_ids = self.env['account.payment'].search([('invoice_ids', '=', self.id)])
            rec.payment_count = len(payment_ids.ids)

    @api.depends('state','payment_state','remaining_value')
    def get_payment_ids(self):
        for rec in self:

            rec.payment_ids_line = []
            rec.is_payment_visible = False
            if rec.state == 'posted' and rec.payment_state!='paid':
                lines=[]
                payment_ids = self.env['account.payment'].search([('state','=','posted'),
                                                                  ('contract_id', '=', rec.contract_id.id)])
                for line in payment_ids:
                    amount =line.amount
                    if not line.invoice_ids and not line.reconciled_bill_ids :
                        if  rec.remaining_value>=amount:
                             rec.payment_ids_line=[(4,line.id,)]
                             rec.is_payment_visible=True

    @api.depends('contract_id.number_of_invoice')
    def _get_last_invoice(self):
        for rec in self:
            rec.is_last=False
            inv_ids = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],order='id desc',limit=1)
            if inv_ids.id ==rec.id:
                rec.is_last = True

    def reset_invoice(self):
        self.state='draft'
        move_ids=self.env['account.move'].search([('invoice_id','=',self.id)])
        for rec in move_ids:
            rec.button_cancel()








    @api.depends('payment_amount')
    def get_remaining(self):
        for rec in self:
            rec.remaining_value=abs(rec.amount_price_total-rec.payment_amount)



    @api.depends('deduction_ids','allowance_ids')
    def _calculate_total_deduction_addition(self):
        for rec in self:
            deduction_value, addition_value = 0, 0
            for ded in rec.deduction_ids:
                deduction_value += ded.current_value
            for allow in rec.allowance_ids:
                addition_value += allow.current_value
            rec.current_total_value_deduction=deduction_value
            rec.current_total_value_addition=addition_value
    @api.depends('current_total_value','deduction_ids','allowance_ids')
    def _get_amount_price_total(self):
        for rec in self:
            deduction_value,addition_value =0,0
            for ded in rec.deduction_ids:
                deduction_value+=ded.current_value
            for allow in rec.allowance_ids:
                addition_value+=allow.current_value
            rec.amount_price_total=rec.current_total_value+addition_value-deduction_value



    @api.depends('project_id')
    def _get_invoice_name(self):
        for rec in self:
            rec.name='INV/'+str(rec.id).zfill(5)
    def get_owner_contract_line(self):

        if self.contract_id:
            lines = []
            invoice_previous = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                                  order='id desc', limit=1)
            last_d = last_a = 0



            for rec in self.contract_id.deduction_ids:


                last_d = last_a = 0
                if invoice_previous:
                    ded_lines = self.env['contract.deduction.lines.invoice'].search(
                        [('invoice_id', '=', invoice_previous.id),
                         ('name', '=', rec.name.id)])
                    for rec in ded_lines:
                        last_d+=rec.value + rec.last_value

                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'deduction',
                    'name': rec.name,
                    'account_id': rec.account_id,
                    'is_precentage': rec.is_precentage,
                    'precentage': rec.precentage,
                    'last_value' : last_d
                }))


            if lines:
                self.deduction_ids = lines
            lines = []
            for record in self.contract_id.allowance_ids:

                last_d = last_a = 0
                if invoice_previous:
                    ded_lines = self.env['contract.addition.lines.invoice'].search(
                        [('invoice_id', '=', invoice_previous.id),
                         ('account_id', '=', rec.account_id.id),
                         ('name', '=', rec.name.id)])
                    for rec in ded_lines:
                        last_a += rec.value + rec.last_value
                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'addition',
                    'name': record.name,
                    'account_id': record.account_id,
                    'is_precentage': record.is_precentage,
                    'precentage': record.precentage,
                    'last_value': last_a
                }))

            if lines:
                self.allowance_ids = lines
            invoice_previous = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                                  order='id desc', limit=1)
            if invoice_previous:
                invoice_ids = []

                for rec in invoice_previous.invoice_line:

                    lines = self.env['account.invoice.line'].search(
                        [('tender_id', '=', rec.tender_id.id), ('invoice_id', '=', invoice_previous.id), ])
                    last_qty, last_total_value = 0, 0
                    for rec in lines:
                        last_qty += rec.quantity
                        last_total_value += rec.total_value
                        invoice_ids.append((0, 0,
                                            {
                                                'tender_id': rec.tender_id.id,
                                                'type': rec.type,
                                                'last_qty': last_qty,
                                                'rate': rec.rate, 'last_total_value': last_total_value,
                                                'quantity': rec.quantity, 'price_unit': rec.price_unit

                                            }))

                self.invoice_line = invoice_ids

    def get_supconstractor_contract_line(self):
        if self.contract_id:
            lines = []
            invoice_previous = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                                  order='id desc', limit=1)
            last_d=last_a=0
            print(">>>>>>>>>>>>>>>>.",invoice_previous)
            for rec in invoice_previous.deduction_ids:
                last_d=last_d+rec.value+rec.last_value
            for rec in invoice_previous.allowance_ids:
                last_a=last_a+rec.value+rec.last_value


            for rec in self.contract_id.deduction_ids:


                last_d = last_a = 0
                if invoice_previous:
                    ded_lines = self.env['contract.deduction.lines.invoice'].search(
                        [('invoice_id', '=', invoice_previous.id),
                         ('name', '=', rec.name.id)])
                    for rec in ded_lines:
                        last_d += rec.value + rec.last_value
                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'deduction',
                    'name': rec.name,
                    'account_id': rec.account_id,
                    'is_precentage': rec.is_precentage,
                    'precentage': rec.precentage,
                    'last_value': last_d
                }))

            if lines:
                self.deduction_ids = lines
            lines = []
            for record in self.contract_id.allowance_ids:

                last_d = last_a = 0
                if invoice_previous:
                    ded_lines = self.env['contract.addition.lines.invoice'].search(
                        [('invoice_id', '=', invoice_previous.id),
                         ('account_id', '=', rec.account_id.id),
                         ('name', '=', rec.name.id)])
                    for rec in ded_lines:
                        last_a += rec.value + rec.last_value
                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'addition',
                    'name': record.name,
                    'account_id': record.account_id,
                    'is_precentage': record.is_precentage,
                    'precentage': record.precentage,
                    'last_value': last_a
                }))

            if lines:
                self.allowance_ids = lines
            invoice_previous = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                                  order='id desc', limit=1)

            if invoice_previous:
                invoice_ids,domain = [],[]

                for rec in invoice_previous.invoice_line:

                    invoice_ids.append((0, 0,
                                            {
                                                'tender_id': rec.tender_id.id,
                                                'type': rec.type,
                                                'last_qty': rec.quantity,
                                                'rate': rec.rate, 'last_total_value': rec.total_value,
                                                'quantity': rec.quantity, 'price_unit': rec.price_unit,
                                                'sub_contarctor_item': rec.sub_contarctor_item.id,
                                                'wbs_item': rec.wbs_item,
                                                'wbs_item_id': rec.wbs_item.id,
                                                'sub_contarctor_item_id': rec.sub_contarctor_item.id,


                                            }))


                self.invoice_line=invoice_ids
                return self.invoice_line

    @api.onchange("contract_id")
    def _get_deduction_allowance(self):

        if self.contract_id.type=='owner':
            self.get_owner_contract_line()
        if self.contract_id.type=='supconstractor':

            self.get_supconstractor_contract_line()


    @api.depends('state')
    def _get_payment_state(self):
        for rec in self:
            rec.payment_state='not_paid'
            if rec.payment_amount == 0:
                rec.payment_state = 'not_paid'
            elif rec.payment_amount < rec.amount_price_total:
                rec.payment_state = 'in_payment'
            elif rec.payment_amount == rec.amount_price_total:
                rec.payment_state = 'paid'
            lines = []

            p_list=[]
            # for p in rec.payment_ids:
            #     p_list.append(p.payment_id.id)





            # if rec.state == 'posted':
                # screen_ids = self.env['account.screen'].search([('invoice_id','=',self.id)])
                # for sr in screen_ids:
                #     sr.unlink()

                # payment_ids = self.env['account.payment'].search([('state','=','posted'),('contract_id', '=', rec.contract_id.id)])
                # for line in payment_ids:
                #     if not line.invoice_ids and not line.reconciled_bill_ids :
                #         if  line.id not in p_list:
                #
                #             lines.append((0, 0, {
                #                 'payment_id': line.id
                #
                #             }))
                #
                #     rec.payment_ids = lines

    @api.depends('invoice_line')
    def _calculate_total_value(self):
        for record in self:
            total_value, last_total_value, current_total_value = 0, 0, 0
            for rec in record.invoice_line:
                total_value += rec.total_value
                last_total_value += rec.last_total_value
                current_total_value += rec.current_total_value
            record.total_value = total_value
            record.last_total_value = last_total_value
            record.current_total_value = current_total_value

    def action_post(self):
        self.state = 'posted'
        self.create_journal_enteries()

    def create_journal_enteries(self):
        lines = self._get_move_line()
        print(">>>>>>>>>xxxx>>>>>>>>>> ", lines)

        journal = ''
        partner_id=''
        if self.type == 'owner':
            if not self.company_id.ks_middle_journal_owner:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_journal_owner.id
            partner_id=self.partner_id.id

        elif self.type == 'supconstractor':
            if not self.company_id.ks_middle_account_sup:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_account_sup.id
            partner_id = self.sub_contactor.id
        move2 = self.env['account.move'].create({'date': datetime.today(),
                                                 'partner_id': partner_id,
                                                 'company_id': self.company_id.id,
                                                 'journal_id': journal,
                                                 'name': self._get_payment_name(journal),
                                                 'project_id':self.project_id.id,
                                                 'line_ids': lines,
                                                 'invoice_id': self.id
                                                 })

    def _get_payment_name(self, journal):
        sequ = self.env['account.move'].search([('journal_id', '=', journal)])
        journal_id = self.env['account.journal'].search([('id', '=', journal)])
        name = journal_id.code + "/" + str(datetime.now().year) + "/" \
               + str(datetime.now().month) + "/" + str(len(sequ) + 1).zfill(4)
        return name
    def _get_move_line(self):
        lines=[]
        debit, credit = 0, 0
        if self.type=='supconstractor':
            for rec in self.deduction_ids:
                credit += round(rec.current_value,2)
                lines.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'credit': round(rec.current_value,2),
                    'debit': 0,
                    'partner_id': self.sub_contactor.id,
                }))
            for rec in self.allowance_ids:
                debit += round(rec.current_value,2)
                lines.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'debit': round(rec.current_value,2),
                    'credit': 0,
                    'partner_id': self.sub_contactor.id,
                }))
        else:
            for rec in self.deduction_ids:
                debit += round(rec.current_value, 2)
                lines.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'debit': round(rec.current_value, 2),
                    'credit': 0,
                    'partner_id': self.partner_id.id,

                }))
            for rec in self.allowance_ids:
                credit += round(rec.current_value, 2)
                lines.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'credit': round(rec.current_value, 2),
                    'debit': 0,
                    'partner_id': self.partner_id.id,

                }))
        if self.type!='supconstractor':
            credit += round(self.current_total_value,2)
            lines.append((0, 0, {
                'account_id': self.contract_id.revenue_account_id.id,
                'credit': round(self.current_total_value,2),
                'debit': 0,
                'partner_id': self.partner_id.id,

            }))
            lines.append((0, 0, {
                'account_id': self.contract_id.account_id.id,
                'credit': 0,
                'debit': round(credit - debit,2),
                'partner_id': self.partner_id.id,
            }))
        elif self.type=='supconstractor':
            print(">>>>>>>>>>>XXX ",self.current_total_value)
            debit += round(self.current_total_value,2)
            lines.append((0, 0, {
                'account_id': self.contract_id.revenue_account_id.id,
                'credit': 0,
                'debit': round(self.current_total_value,2),
                'partner_id': self.sub_contactor.id,
            }))
            print(debit, ">>>>>>>>>>>XXX ", credit)
            print(debit-credit, ">>>>>>>>>>>XXX ", round(debit-credit,2))
            lines.append((0, 0, {
                'account_id': self.contract_id.account_id.id,
                'credit': round(debit-credit,2),
                'debit':  0,
                'partner_id': self.sub_contactor.id,
            }))




        return lines
    def select_tender_ids(self):
        view_form = self.env.ref('construction.view_move_construction_pop_wizard_pop')

        self.is_tender = True

        # self._get_tender_ids()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender',
            'view_mode': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'invoice.tender.wizard',
            'target': 'new',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id, 'default_project_id': self.project_id.id}

        }
    def select_contract_lines_ids(self):
        view_form = self.env.ref('construction.view_move_construction_pop_wizard_pop_subcontractor')

        self.is_tender = True

        # self._get_tender_ids()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender',
            'view_mode': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'invoice.tender.wizard',
            'target': 'new',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id, 'default_project_id': self.project_id.id,
                        'default_contract_id':self.contract_id.id}

        }

    def action_payment(self):
        view_form = self.env.ref('construction.payment_inherited_form_invoice')
        payment_id = self.env['account.payment'].search([('invoice_ids', '=', self.id)])
        amount = 0
        for rec in payment_id:
            amount += rec.amount
        journal,partner_id,payment_type,partner_type = '','','',''
        if self.type == 'owner':
            if not self.company_id.ks_middle_journal_owner:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_journal_owner.id
            partner_id = self.partner_id.id
            payment_type='inbound'
            partner_type='customer'

        elif self.type == 'supconstractor':
            if not self.company_id.ks_middle_account_sup:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_account_sup.id
            partner_id = self.contract_id.sub_contactor.id
            payment_type = 'outbound'
            partner_type='supplier'



        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'account.payment',
            'target': 'new',
            'context': {'default_invoice_ids': self.id, 'default_journal_id': journal,
                        'default_payment_type':payment_type,
                        'default_partner_type':partner_type,
                        'default_partner_id': partner_id, 'default_amount': self.remaining_value}

        }

    def view_journal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('invoice_id', '=', self.id)]

        }

    def view_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'target': 'current',
            'domain': [('invoice_ids', '=', self.id)]
        }
    def unlink(self):
        for rec in self:
            if rec.state=='posted':
                raise ValidationError("You Cann't posted invoice")
            for recr in rec.invoice_line:
                recr.unlink()
            for ded in rec.deduction_ids:
                ded.unlink()
            for all in rec.allowance_ids:
                    all.unlink()
        res =super(Invoice, self).unlink()
        return res



class InvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _order = 'tender_id'

    project_id = fields.Many2one(related='invoice_id.project_id',store=True,index=True)
    tender_id = fields.Many2one('construction.tender', string="Tender ID")
    # name = fields.Text(related='tender_id.description', string="Description")  #Abdulrhman comment
    name = fields.Text(string="Description")

    @api.onchange('tender_id')
    def change_tender_id(self):
        self.name = self.tender_id.description

    code = fields.Char(related='tender_id.code', string="Code")
    item = fields.Many2one(related='tender_id.item', string='Item',store=True,index=True)
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure",store=True,index=True)
    sub_type = fields.Selection(related='tender_id.type', string='Type')
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    contract_qty = fields.Float(compute='get_contract_qty', string="contract quantity",store=True,index=True)
    last_qty = fields.Float(string="Previous quantity")
    current_qty = fields.Float("Current Quantity")
    value = fields.Float(compute="_get_value_line", striing="Value")
    rate = fields.Integer("Rate",default='100')
    total_value = fields.Float("Total Value", compute='_get_total_value',store=True,index=True)
    last_total_value = fields.Float("Total Previous Value")
    current_total_value = fields.Float("Total Current Value", compute='_get_total_current_value',store=True,index=True)
    notes = fields.Char("Notes")
    quantity = fields.Float("Quantity", compute='get_total_quantity')
    price_unit = fields.Float(compute='get_contract_qty', string="Price Unit")
    project_id = fields.Many2one(comodel_name='project.project', string='Project', related="invoice_id.project_id",
                                 store=True)
    invoice_id = fields.Many2one("account.invoice")
    date = fields.Date(related='invoice_id.date',store=True,index=True)

    partner_id = fields.Many2one(related="invoice_id.partner_id",store=True, index=True)


    move_id = fields.Many2one("account.move")
    wbs_item_id = fields.Char(string="WBS-item Id")
    wbs_item = fields.Many2one('wbs.item.line', string="WBS-item",domain="[('id','=',wbs_item_id)]")
    sub_contarctor_item_id = fields.Char('construction subconstractor ID')
    sub_contarctor_item = fields.Many2one('construction.subconstractor',domain="[('id','=',sub_contarctor_item_id)]")



    @api.depends('current_qty', 'last_qty')
    def get_total_quantity(self):
        for rec in self:
            rec.quantity = rec.current_qty + rec.last_qty

    @api.depends('code')
    def get_contract_qty(self):
        for rec in self:
            qty = self.env['construction.contract.line'].search([('contract_id', '=', rec.invoice_id.contract_id.id)
                                                                    , ('code', '=', rec.code)],
                                                                limit=1)
            if rec.invoice_id.type == 'supconstractor':
                qty = self.env['construction.contract.line'].search(
                    [('sup_contract_id', '=', rec.invoice_id.contract_id.id)
                        , ('tender_id', '=', rec.tender_id.id)],
                    limit=1)

            if qty:

                rec.contract_qty = qty.qty
                rec.price_unit = qty.price_unit
                # if rec.tender_id:
                #      rec.name = rec.tender_id.description
            else:
                rec.contract_qty = 0
                rec.price_unit = 0

    @api.model
    def create(self, vals):

        res = super(InvoiceLine, self).create(vals)

        move_ids = self.env['account.invoice'].search(
            [('id', '!=', res.invoice_id.id), ('contract_id', '=', res.invoice_id.contract_id.id)],
            order='id desc', limit=1)
        domain=[]

        if res.invoice_id.contract_id.type=='owner':
            lines = self.env['account.invoice.line'].search(
                [('tender_id', '=', res.tender_id.id), ('invoice_id', '=', move_ids.id), ])
            last_qty, last_total_value = 0, 0
            for rec in lines:
                last_qty += rec.quantity
                last_total_value += rec.total_value

            res.last_qty = last_qty
            res.last_total_value = last_total_value
        if res.invoice_id.contract_id.type == 'supconstractor':
            domain.append(('tender_id', '=', res.tender_id.id))
            domain.append(('invoice_id', '=', move_ids.id))

            if res.wbs_item:
                domain.append(('wbs_item','=',res.wbs_item.id))
            if res.sub_contarctor_item:
                domain.append(('sub_contarctor_item','=',res.sub_contarctor_item.id))
            lines = self.env['account.invoice.line'].search(domain )

            last_qty, last_total_value = 0, 0
            for rec in lines:
                last_qty += rec.quantity
                last_total_value += rec.total_value

            res.last_qty = last_qty
            res.last_total_value = last_total_value

        return res

    @api.depends('total_value', 'last_total_value')
    def _get_total_current_value(self):
        for rec in self:
            rec.current_total_value = rec.total_value - rec.last_total_value

    @api.depends('rate', 'value')
    def _get_total_value(self):
        for rec in self:
            if rec.value > 0:
                rec.total_value = (rec.rate / 100) * rec.value
            else:
                rec.total_value = 0

    @api.depends('price_unit', 'quantity')
    def _get_value_line(self):
        for rec in self:
            rec.value = rec.price_unit * rec.quantity





    @api.onchange('current_qty')
    def _onchange_current_qty(self):
        if self.current_qty > self.contract_qty:
            raise ValidationError("Current Qty must be less than or equal Contarct Qty ...!")
    @api.onchange('quantity')
    def _onchange_q(self):
        if self.quantity:
            self.current_qty=self.quantity-self.last_qty
    def write(self,vals):
        print(vals)

        if 'quantity' in vals:

            vals['current_qty']=vals['quantity']-self.last_qty
        res = super(InvoiceLine, self).write(vals)
        return res


