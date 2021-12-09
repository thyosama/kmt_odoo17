from datetime import datetime

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from json import dumps
import json

class Move(models.Model):
    _inherit = 'account.move'
    invoice_id = fields.Many2one('account.invoice', string="Invoice")

class deduction(models.Model):
    _inherit = 'contract.deduction.lines.invoice'
    move_id = fields.Many2one("account.move")
class Additional(models.Model):
    _inherit = 'contract.addition.lines.invoice'
    move_id = fields.Many2one("account.move")
# class Invoice_line(models.Model):
#     _inherit = 'account.invoice.line'
#     move_id = fields.Many2one("account.move")


class Invoice(models.Model):
    _inherit = 'account.move'
    #name = fields.Char(compute="_get_invoice_name",string="Name")
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    type_move = fields.Selection([('process', 'Process'), ('final', 'Final')], string="Type")
    contract_id = fields.Many2one("construction.contract", string="Contract")
    contract_date = fields.Date(related='contract_id.date', string="Contract Date", store=True, index=True)
    number_manual = fields.Char("Manual number")
    project_id = fields.Many2one(related='contract_id.project_id', string="Project",store=True,index=True)
    partner_id = fields.Many2one(related="project_id.partner_id", string="Customer", store=True, index=True)
    sub_contactor = fields.Many2one(related='contract_id.sub_contactor', string="sub contractor Name")
    deduction_ids = fields.One2many("contract.deduction.lines.invoice", "move_id",
                                    string="Deductions", domain=[('type', '=', 'deduction')])
    allowance_ids = fields.One2many("contract.addition.lines.invoice", "move_id",
                                    string="Additions", domain=[('type', '=', 'addition')])
    is_tender = fields.Boolean(default=False)
    invoice_line = fields.One2many('account.invoice.line', 'invoice_id', string="Lines")
    date = fields.Date(string="Date", default=datetime.today())
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string="State", default='draft')
    total_value = fields.Float("Total Value", compute='_calculate_total_value')
    last_total_value = fields.Float("Total last Value", compute='_calculate_total_value')
    current_total_value = fields.Float("Total Current Value", compute='_calculate_total_value',store=True,index=True)
    current_total_value_deduction = fields.Float("current deduction", compute='_calculate_total_deduction_addition',store=True,index=True)
    current_total_value_addition = fields.Float("Current Additional", compute='_calculate_total_deduction_addition',store=True,index=True)
    payment_amount = fields.Float("payment Amount")
    payment_count = fields.Integer("payment Count")
    payment_state = fields.Selection([('not_paid', 'Not paid'), ('in_payment', 'Partially Paid'), ('paid', 'Paid')]
                                     , compute='_get_payment_state')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    amount_price_total = fields.Float(compute='_get_amount_price_total')
    remaining_value = fields.Float("remaining Value",compute='get_remaining')
    is_last = fields.Boolean(compute='_get_last_invoice')
    invoice_outstanding_credits_debits_widget = fields.Text(
        compute='_compute_payments_widget_to_reconcile_info')

    @api.depends('contract_id.number_of_invoice')
    def _get_last_invoice(self):
        for rec in self:
            rec.is_last=False
            inv_ids = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)])
            number_of_invoice=0
            if inv_ids:
                number_of_invoice=len(inv_ids)
            inv_ids = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                         order='id desc',limit=1)
            if number_of_invoice==self.contract_id.number_of_invoice and inv_ids.id==self.id:
                rec.is_last = True

    def reset_invoice(self):
        self.state='draft'
        move_ids=self.env['account.move'].search([('invoice_id','=',self.id)])
        for rec in move_ids:
            rec.button_cancel()







    @api.depends('payment_amount')
    def get_remaining(self):
        for rec in self:
            rec.remaining_value=rec.amount_price_total-rec.payment_amount


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

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id','amount_price_total')
    def _compute_amount(self):
        res = super(Invoice, self)._compute_amount()
        for rec in self:
            if rec.amount_price_total >0:
                    rec.amount_total = rec.amount_price_total

        return res



    @api.depends('current_total_value','deduction_ids','allowance_ids')
    def _get_amount_price_total(self):
        for rec in self:
            deduction_value,addition_value =0,0
            for ded in rec.deduction_ids:
                deduction_value+=ded.current_value
            for allow in rec.allowance_ids:
                addition_value+=allow.current_value
            rec.amount_price_total=rec.current_total_value+addition_value-deduction_value
            rec.amount_total = rec.amount_price_total






    @api.depends('project_id')
    def _get_invoice_name(self):
        for rec in self:
            rec.name='INV/'+str(rec.id).zfill(5)

    @api.onchange("contract_id")
    def _get_deduction_allowance(self):

        if self.contract_id:
            lines = []
            for rec in self.contract_id.deduction_ids:
                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'deduction',
                    'name': rec.name,
                    'account_id': rec.account_id,
                    'is_precentage': rec.is_precentage,
                    'precentage': rec.precentage,
                }))

            if lines:
                self.deduction_ids = lines
            lines = []
            for record in self.contract_id.allowance_ids:
                lines.append((0, 0, {
                    'sub_type': self.type,
                    'type': 'addition',
                    'name': record.name,
                    'account_id': record.account_id,
                    'is_precentage': record.is_precentage,
                    'precentage': record.precentage,
                }))

            if lines:
                self.allowance_ids = lines
            invoice_previous = self.env['account.invoice'].search([('contract_id', '=', self.contract_id.id)],
                                                                  order='id desc', limit=1)
            if invoice_previous:
                invoice_ids = []
                print(">>>>>>>>>>>>>>>>>>>.....",invoice_previous)
                for rec in invoice_previous.invoice_line:

                    lines = self.env['account.invoice.line'].search(
                        [('tender_id', '=', rec.tender_id.id), ('invoice_id', '=', invoice_previous.id), ])
                    last_qty, last_total_value = 0, 0
                    for rec in lines:
                        last_qty += rec.quantity
                        last_total_value += rec.total_value
                    if rec.invoice_id.type=='supconstractor':
                        invoice_ids.append((0, 0,
                                            {
                                                'tender_id': rec.tender_id.id,
                                                'type': rec.type,
                                                'last_qty': last_qty,
                                                'rate': 100, 'last_total_value': last_total_value,
                                                'quantity': rec.quantity, 'price_unit': rec.price_unit,'sub_contarctor_item':rec.sub_contarctor_item,
                                                'wbs_item':rec.wbs_item

                                            }))
                    else:

                         invoice_ids.append((0, 0,
                                        {
                                            'tender_id': rec.tender_id.id,
                                            'type': rec.type,
                                            'last_qty': last_qty,
                                            'rate': 100, 'last_total_value': last_total_value,
                                            'quantity': rec.quantity, 'price_unit': rec.price_unit

                                        }))

                self.invoice_line = invoice_ids

    @api.depends('payment_amount')
    def _get_payment_state(self):
        for rec in self:
            if rec.payment_amount == 0:
                rec.payment_state = 'not_paid'
            elif rec.payment_amount < rec.amount_price_total:
                rec.payment_state = 'in_payment'
            elif rec.payment_amount == rec.amount_price_total:
                rec.payment_state = 'paid'

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



        journal = ''
        if self.type == 'owner':
            if not self.company_id.ks_middle_journal_owner:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_journal_owner.id

        elif self.type == 'supconstractor':
            if not self.company_id.ks_middle_account_sup:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_account_sup.id
        self.date =datetime.today()
        self.company_id =self.company_id
        self.journal_id =journal
        self.name =self._get_payment_name(journal)
        self.line_ids=lines
        # move2 = self.env['account.move'].create({'date': datetime.today(),
        #                                          'partner_id': self.partner_id.id or '',
        #
        #                                          'company_id': self.company_id.id,
        #                                          'journal_id': journal,
        #                                          'name': self._get_payment_name(journal),
        #                                          'line_ids': lines,
        #                                          'invoice_id': self.id
        #
        #                                          })

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
                    'partner_id': self.partner_id.id,

                }))
            for rec in self.allowance_ids:
                debit += round(rec.current_value,2)
                lines.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'debit': round(rec.current_value,2),
                    'credit': 0,
                    'partner_id': self.partner_id.id,

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
            debit += round(self.current_total_value,2)

            lines.append((0, 0, {
                'account_id': self.contract_id.revenue_account_id.id,
                'credit': round(self.current_total_value,2),
                'debit': 0,
                'partner_id': self.partner_id.id,

            }))
            lines.append((0, 0, {
                'account_id': self.contract_id.account_id.id,
                'credit': 0,
                'debit':  round(debit-credit,2),
                'partner_id': self.partner_id.id,

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

    def action_payment(self):
        view_form = self.env.ref('construction.payment_inherited_form_invoice')
        payment_id = self.env['account.payment'].search([('invoice_ids', '=', self.id)])
        amount = 0
        for rec in payment_id:
            amount += rec.amount
        journal,partner_id = '',''
        if self.type == 'owner':
            if not self.company_id.ks_middle_journal_owner:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_journal_owner.id
            partner_id = self.partner_id.id

        elif self.type == 'supconstractor':
            if not self.company_id.ks_middle_account_sup:
                raise ValidationError("Please Select journal")
            journal = self.company_id.ks_middle_account_sup.id
            partner_id = self.contract_id.sub_contactor.id



        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'account.payment',
            'target': 'new',
            'context': {'default_invoice_ids': self.id, 'default_journal_id': journal,
                        'default_partner_id': partner_id, 'default_amount': self.remaining_value}

        }

    def view_journal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', '=', self.id)]

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

        if self.state=='posted':
            raise ValidationError("You Cann't posted invoice")
        for rec in self.invoice_line:
            rec.unlink()
        res =super(Invoice, self).unlink()
        return res



class InvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _order = 'tender_id'

    project_id = fields.Many2one(related='invoice_id.project_id',store=True,index=True)
    tender_id = fields.Many2one('construction.tender', string="Tender ID")
    name = fields.Char(related='tender_id.description', string="Description")
    code = fields.Char(related='tender_id.code', string="Code")
    item = fields.Many2one(related='tender_id.item', string='Item')
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    sub_type = fields.Selection(related='tender_id.type', string='Type')
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    contract_qty = fields.Float(compute='get_contract_qty', string="contract quantity",store=True,index=True)
    last_qty = fields.Float(string="Last quantity")
    current_qty = fields.Float("Current Quantity")
    value = fields.Float(compute="_get_value_line", striing="Value")
    rate = fields.Integer("Rate",default='100')
    total_value = fields.Float("Total Value", compute='_get_total_value')
    last_total_value = fields.Float("Total last Value")
    current_total_value = fields.Float("Total Current Value", compute='_get_total_current_value',store=True,index=True)
    notes = fields.Char("Notes")
    quantity = fields.Float("Quantity", compute='get_total_quantity')
    price_unit = fields.Float(compute='get_contract_qty', string="Price Unit")
    project_id = fields.Many2one(comodel_name='project.project', string='Project', related="invoice_id.project_id",
                                 store=True)
    invoice_id = fields.Many2one("account.move")

    partner_id = fields.Many2one(related="invoice_id.partner_id",store=True, index=True)


    move_id = fields.Many2one("account.move")
    wbs_item = fields.Many2one('wbs.item.line', string="WBS-item",domain="[('project_id', '=', project_id)]")
    sub_contarctor_item = fields.Many2one('construction.subconstractor',string="SubConstractor",
                                          domain="[('tender_id','=',tender_id)]")

    # @api.onchange('sub_contarctor_item', 'tender_id','code')
    # @api.depends('sub_contarctor_item', 'tender_id','code')
    # def _onchange_tender_id(self):
    #     print("**************************************************************************")
    #
    #     if self.tender_id:
    #
    #         sub_contractors = []
    #         job_cost_id = self.env['construction.job.cost'].search([
    #             ('project_id', '=', self.project_id.id),
    #             ('tender_id', '=', self.tender_id.id),
    #         ])
    #         print("<<>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<",job_cost_id)
    #         for job_cost in job_cost_id:
    #             print(job_cost, "Line", job_cost.subconstractor_ids)
    #             for line in job_cost.subconstractor_ids:
    #                 sub_contractors.append(line.id)
    #
    #         print("!!!!!!!!!!!!!!!!11",sub_contractors)
    #
    #
    #         return {'domain': {'sub_contarctor_item': [('id', 'in', sub_contractors)]}}



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

        lines = self.env['account.invoice.line'].search(
            [('tender_id', '=', res.tender_id.id), ('invoice_id', '=', move_ids.id), ])
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

    @api.onchange('tender_id')
    def _get_line_data(self):

        ids = []
        tender = self.env['construction.contract.line'].search([('contract_id', '=', self.invoice_id.contract_id.id)])
        for rec in tender:
            if rec.tender_id.type == 'transcation':
                ids.append(rec.tender_id.id)

        domain = {'tender_id': [('id', 'in', ids)]}

        return {'domain': domain}

    @api.onchange('current_qty')
    def _onchange_current_qty(self):
        if self.current_qty > self.contract_qty:
            raise ValidationError("Current Qty must be less than or equal Contarct Qty")
