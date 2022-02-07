# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LetterGuranteeSetting(models.Model):
    _name = 'guarantee.letter.setting'
    _rec_name='name'

    name = fields.Char('Name')
    
    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Debit",
        required=True,
        )

    letter_type = fields.Selection(
        string="Letter Type",
        selection=[
            ('premium', 'Premium'), 
            ('final', 'Final'),
            ('deposit', 'Deposit'),
            ]
        )

    bank_expense_account_id = fields.Many2one(
        comodel_name='account.account', 
        string="Account Expenses Debit",
        required=True,
        )