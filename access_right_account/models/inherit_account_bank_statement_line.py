from odoo import models, api

class AccountBankStatementLineInherit(models.Model):
    _inherit = "account.bank.statement.line"

    @api.model_create_multi
    def create(self, values):
        res=super(AccountBankStatementLineInherit, self).create(values)
        res.move_id.state='draft'
        return res
