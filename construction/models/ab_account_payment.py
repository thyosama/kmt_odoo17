from odoo import fields, models, api
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    type_contract = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Contract Type",compute='get_type_contract')

    contract_id = fields.Many2one('construction.contract', string="contract",
                                              domain="[('state','=','confirm'),('type', '=', type_contract)]")

    invoice_ids = fields.Many2one('account.invoice')
    x = fields.Char()
    @api.depends('payment_type')
    def get_type_contract(self):
        for rec in self:
            rec.type_contract=''
            if rec.payment_type=='outbound':
                rec.type_contract='supconstractor'
            elif rec.payment_type!='outbound':
                rec.type_contract = 'owner'
    @api.onchange('contract_id')
    def get_partner(self):
        if self.contract_id:
             if self.type_contract=='owner' :
                 self.partner_id = self.contract_id.parner_id.id
             if self.type_contract=='supconstractor' :
                 self.partner_id = self.contract_id.sub_contactor.id


    @api.model
    def create(self,vals):
        res = super(AccountPayment,self).create(vals)
        if 'invoice_ids' in vals:

            if vals.get('invoice_ids'):
                invoice_id=self.env['account.invoice'].search([('id','=',vals.get('invoice_ids'))])


                if invoice_id.payment_amount+res.amount > round(invoice_id.amount_price_total,2):
                    raise ValidationError("Amount must be less Current Amount")

                invoice_id.payment_amount+= res.amount
                invoice_id.payment_count+=1
        return res
    def write(self,vals):
        res=super(AccountPayment, self).write(vals)
        if 'invoice_ids' in vals:
            invoice_id=self.env['account.invoice'].search([('id','=',vals.get('invoice_ids'))])


            if invoice_id.payment_amount+self.amount > invoice_id.amount_price_total:
                raise ValidationError("Amount must be less Current Amount")

            invoice_id.payment_amount+= self.amount
            invoice_id.payment_count+=1
        return res
    def add_invoice(self):
        inv = self.env.context.get('invoice_ids')
        self.payment_id.invoice_ids = inv
        self.invoice_ids=inv
        self.invoice_id._get_payment_state()
