# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SendGurantee(models.Model):
    _name = 'guarantee.send'
    _rec_name = 'number'

    number = fields.Char('Sequence')
    letter_guarantee_id = fields.Many2one(comodel_name='guarantee.letter', string="Gurantee Letter")
    
    partner_id = fields.Many2one(related='letter_guarantee_id.partner_id', string='Customer', comodel_name='res.partner')
    
    journal_id = fields.Many2one(related='letter_guarantee_id.journal_id', string='journal')
    letter_type = fields.Selection(string="Letter Type", related='letter_guarantee_id.letter_type')
    letter_amount = fields.Float('Letter Amount', related='letter_guarantee_id.letter_amount')
    bank_expense_account_id = fields.Many2one('account.account', string="Account Expenses Debit")

    transaction_date = fields.Date(string="Transaction Date", related='letter_guarantee_id.transaction_date')
    start_date = fields.Date(string="Start Date", related='letter_guarantee_id.start_date')
    end_date = fields.Date(string="End Date", related='letter_guarantee_id.end_date')
    letter_number = fields.Char('Letter Number', related='letter_guarantee_id.letter_number')
    cheque_no =fields.Char('Cheque No')
    cheque_amount =fields.Char('Cheque Amount')
    note=fields.Text('Note')



    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('guarantee.send') or '/'
        vals['number'] = seq
        return super(SendGurantee, self).create(vals)

