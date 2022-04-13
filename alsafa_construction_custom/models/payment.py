from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Payment(models.Model):
    _inherit = 'account.payment'
    @api.constrains('project_id','contract_id')
    def _check_project_contract(self):
        if self.contract_id and self.project_id:
            if self.contract_id.project_id!=self.project_id:
                raise  ValidationError("You select Project and project's contract are different")


class Invoice(models.Model):
    _inherit = "account.invoice"
    # def action_payment(self):
    #     view_form = self.env.ref('construction.payment_inherited_form_invoice')
    #     payment_id = self.env['account.payment'].search([('invoice_ids', '=', self.id)])
    #     amount = 0
    #     for rec in payment_id:
    #         amount += rec.amount
    #     journal,partner_id, = '',''
    #     if self.type == 'owner':
    #         if not self.company_id.ks_middle_journal_owner:
    #             raise ValidationError("Please Select journal")
    #         journal = self.company_id.ks_middle_journal_owner.id
    #         partner_id = self.partner_id.id
    #
    #     elif self.type == 'supconstractor':
    #         if not self.company_id.ks_middle_account_sup:
    #             raise ValidationError("Please Select journal")
    #         journal = self.company_id.ks_middle_account_sup.id
    #         partner_id = self.contract_id.sub_contactor.id
    #
    #
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Payment',
    #         'view_mode': 'form',
    #         'views': [(view_form.id, 'form')],
    #         'res_model': 'account.payment',
    #         'target': 'new',
    #         'context': {'default_invoice_ids': self.id, 'default_journal_id': journal,'default_project_id':self.project_id.id,
    #                     'default_partner_id': partner_id, 'default_amount': self.remaining_value}
    #
    #     }

