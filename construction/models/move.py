from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class account_move_line(models.Model):
    _inherit = 'account.move.line'
    project_id= fields.Many2one(comodel_name='project.project', string='Project',related="move_id.project_id",store=True,index=True)
    job_id = fields.Many2one('construction.job.cost', string="Break Down ", domain="[('project_id','=',project_id)]")
    item_ids = fields.Many2many('product.item', "item_id", "line_ids", string='Item', compute='_get_item_list')
    item = fields.Many2one('product.item', string='Item', domain="[('id','in',item_ids)]")

    @api.depends('project_id')
    def _get_item_list(self):
        ids = []
        for rec in self:
            rec.item_ids = []
            if rec.project_id:
                pro = self.env['project.project'].search([('id', '=', rec.project_id.id)])
                for ten in pro.tender_ids:
                    rec.item_ids = [(4, ten.item.id)]


class account_move(models.Model):
    _inherit = 'account.move'
    project_id = fields.Many2one(comodel_name='project.project', string='Project', )

    @api.model
    def create(self, vals):

        res = super(account_move, self).create(vals)

        if res.stock_move_id:
            if res.stock_move_id.picking_id.project_id:
                res.project_id = res.stock_move_id.picking_id.project_id

        return res





# class Invoice(models.Model):
#     _inherit = 'account.move'
#     invoice_id = fields.Many2one('account.invoice', string="Invoice")
#     # type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'supconstractor')], string="Type" )
#     # type_move= fields.Selection([('process','Process'),('final','Final')],string="Type")
#     # contract_id = fields.Many2one("construction.contract", string="Contract")
#     # number_manual =fields.Char("Manual number")
#     # project_id = fields.Many2one(related='contract_id.project_id', string="Project")
#     # partner_id = fields.Many2one(related="project_id.partner_id", string="Customer", store=True, index=True)
#     # deduction_ids = fields.One2many("contract.deduction.lines.invoice","move_id",
#     #                                 string="Deductions",domain=[('type','=','deduction')])
#     # allowance_ids = fields.One2many("contract.addition.lines.invoice","move_id",
#     #                                 string="Additions",domain=[('type','=','addition')])
#     # is_tender = fields.Boolean(default=False)
#     # invoice_line = fields.One2many('account.invoice.line','move_id',string="Lines")
#     # date = fields.Date(string="Date",default=datetime.today())
#     # state = fields.Selection([('draft','Draft'),('posted','Posted')],string="State",default='draft')
#     # total_value = fields.Float("Total Value", compute='_calculate_total_value')
#     # last_total_value = fields.Float("Total last Value",compute='_calculate_total_value')
#     # current_total_value = fields.Float("Total Current Value", compute='_calculate_total_value')
#     # # payment_amount = fields.Float("payment Amount")
#     # # payment_count = fields.Integer("payment Count")
#     # # payment_state = fields.Selection([('not_paid','Not paid'),('in_payment','In Payment'),('paid','Paid')]
#     # #                                  ,compute='_get_payment_state')
#     # # company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
#     #
#     #
#     # @api.onchange("contract_id")
#     # def _get_deduction_allowance(self):
#     #
#     #     if self.contract_id:
#     #         lines=[]
#     #         for rec in self.contract_id.deduction_ids:
#     #             print(">>>>>>>>>>>>>@@@@@@@@@22",rec)
#     #             lines.append((0,0,{
#     #                 'sub_type':self.type,
#     #                 'type':'deduction',
#     #                 'name':rec.name,
#     #                 'account_id':rec.account_id,
#     #                 'is_precentage':rec.is_precentage,
#     #                 'precentage':rec.precentage,
#     #             }))
#     #
#     #
#     #
#     #         if lines:
#     #
#     #             self.deduction_ids = lines
#     #         lines=[]
#     #         for record in self.contract_id.allowance_ids:
#     #             lines.append((0, 0, {
#     #                 'sub_type':self.type,
#     #                 'type': 'addition',
#     #                 'name': record.name,
#     #                 'account_id': record.account_id,
#     #                 'is_precentage': record.is_precentage,
#     #                 'precentage': record.precentage,
#     #             }))
#     #
#     #         if lines:
#     #
#     #             self.allowance_ids = lines
#     #
#     #
#     #
#     #
#     # @api.depends('payment_amount')
#     # def _get_payment_state(self):
#     #     for rec in self:
#     #         if rec.payment_amount==0:
#     #             rec.payment_state='not_paid'
#     #         elif rec.payment_amount<rec.current_total_value:
#     #             rec.payment_state='in_payment'
#     #         elif rec.payment_amount==rec.current_total_value:
#     #             rec.payment_state='paid'
#     #
#     # @api.depends('invoice_line')
#     # def _calculate_total_value(self):
#     #     for record in self:
#     #         total_value,last_total_value,current_total_value=0,0,0
#     #         for rec in record.invoice_line:
#     #             total_value += rec.total_value
#     #             last_total_value += rec.last_total_value
#     #             current_total_value += rec.current_total_value
#     #         record.total_value=total_value
#     #         record.last_total_value=last_total_value
#     #         record.current_total_value=current_total_value
#     #
#     # def action_post_construct(self):
#     #     self.state='posted'
#     #     self.create_journal_enteries()
#     # def create_journal_enteries(self):
#     #     lines=[]
#     #     # first = {
#     #     #     'account_id': self.journal_id.default_account_id.id,
#     #     #     'partner_id': self.partner_id.id,
#     #     #     'name': self.name,
#     #     #     'date_maturity': self.effective_date,
#     #     #     'debit': 0,
#     #     #     'credit': self.amount,
#     #     # }
#     #     debit,credit=0,0
#     #     for rec in self.deduction_ids:
#     #         credit+=rec.current_value
#     #         lines.append((0,0,{
#     #             'account_id':rec.account_id.id,
#     #             'credit':rec.current_value,
#     #             'debit':0,
#     #             'partner_id': self.partner_id.id,
#     #
#     #         }))
#     #     for rec in self.allowance_ids:
#     #         debit += rec.current_value
#     #         lines.append((0,0,{
#     #             'account_id':rec.account_id.id,
#     #             'debit':rec.current_value,
#     #             'credit':0,
#     #             'partner_id': self.partner_id.id,
#     #
#     #         }))
#     #     credit += self.current_total_value
#     #     lines.append((0, 0, {
#     #         'account_id': self.contract_id.account_id.id,
#     #         'credit': self.current_total_value,
#     #         'debit': 0,
#     #         'partner_id': self.partner_id.id,
#     #
#     #     }))
#     #     lines.append((0, 0, {
#     #         'account_id': self.contract_id.revenue_account_id.id,
#     #         'credit': 0,
#     #         'debit': credit-debit,
#     #         'partner_id': self.partner_id.id,
#     #
#     #     }))
#     #     journal=''
#     #     if self.type=='owner':
#     #         if not self.company_id.ks_middle_journal_owner:
#     #             raise ValidationError("Please Select journal")
#     #         journal=self.company_id.ks_middle_journal_owner.id
#     #
#     #     elif self.type=='supconstractor':
#     #         if not self.company_id.ks_middle_account_sup:
#     #             raise ValidationError("Please Select journal")
#     #         journal = self.company_id.ks_middle_account_sup.id
#     #     self.journal_id = journal
#     #
#     #     # move2 = self.env['account.move'].create({'date': datetime.today(),
#     #     #                                          'partner_id': self.partner_id.id or '',
#     #     #
#     #     #                                          'company_id': self.company_id.id,
#     #     #                                          'journal_id': journal,
#     #     #                                          'name': self._get_payment_name(journal),
#     #     #                                          'line_ids': lines,
#     #     #                                          'invoice_id':self.id
#     #     #
#     #     #
#     #     #
#     #     #                                          })
#     #
#     # def _get_payment_name(self,journal):
#     #     sequ = self.env['account.move'].search([('journal_id','=',journal)])
#     #     journal_id = self.env['account.journal'].search([('id','=',journal)])
#     #     name = journal_id.code+"/"+str(datetime.now().year)+"/"\
#     #            +str(datetime.now().month)+"/"+str(len(sequ)+1).zfill(4)
#     #     return name
#     # def select_tender_ids(self):
#     #     view_form = self.env.ref('construction.view_move_construction_pop_wizard')
#     #
#     #     self.is_tender=True
#     #
#     #     # self._get_tender_ids()
#     #     return {
#     #         'type': 'ir.actions.act_window',
#     #         'name': 'Tender',
#     #         'view_mode': 'form',
#     #         'views': [(view_form.id, 'form')],
#     #         'res_model': 'invoice.tender.wizard',
#     #         'target': 'new',
#     #         'domain':[('invoice_id','=',self.id)],
#     #         'context':{'default_invoice_id':self.id,'default_project_id':self.project_id.id}
#     #
#     #     }
#     #
#     #
#     # def action_payment(self):
#     #     view_form = self.env.ref('construction.payment_inherited_form_invoice')
#     #     payment_id = self.env['account.payment'].search([('move_id','=',self.id)])
#     #     amount=0
#     #     for rec in payment_id:
#     #         amount+=rec.amount
#     #     journal=''
#     #     if self.type=='owner':
#     #         if not self.company_id.ks_middle_journal_owner:
#     #             raise ValidationError("Please Select journal")
#     #         journal=self.company_id.ks_middle_journal_owner.id
#     #
#     #     elif self.type=='supconstractor':
#     #         if not self.company_id.ks_middle_account_sup:
#     #             raise ValidationError("Please Select journal")
#     #         journal = self.company_id.ks_middle_account_sup.id
#     #
#     #
#     #
#     #     return {
#     #         'type': 'ir.actions.act_window',
#     #         'name': 'Payment',
#     #         'view_mode': 'form',
#     #         'views': [(view_form.id, 'form')],
#     #         'res_model': 'account.payment',
#     #         'target': 'new',
#     #         'context': {'default_invoice_ids': self.id,'default_journal_id':journal,
#     #                     'default_partner_id':self.partner_id.id,'default_amount':self.current_total_value-amount}
#     #
#     #     }
#     # def view_payment(self):
#     #     return {
#     #         'type': 'ir.actions.act_window',
#     #         'name': 'Payment',
#     #         'view_mode': 'tree,form',
#     #         'res_model': 'account.payment',
#     #         'target': 'current',
#     #         'domain':[('invoice_ids','=',self.id)]
#     #
#     #     }
