from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    default_account_id = fields.Many2one(comodel_name='account.account', check_company=True, copy=False,
                                         ondelete='restrict', string='Default Account',
                                         domain="[('deprecated', '=', False), ('company_id', '=', company_id),('user_type_id.type', 'in', ['other', 'liquidity'])]")

    payment_debit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        help="Incoming payments entries triggered by invoices/refunds will be posted on the Outstanding Receipts Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Receipts Account instead of the "
             "receivable account.", string='Outstanding Receipts Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), ]")

    payment_credit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        help="Outgoing payments entries triggered by bills/credit notes will be posted on the Outstanding Payments Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Payments Account instead of the "
             "payable account.", string='Outstanding Payments Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable'))]")
