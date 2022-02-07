# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RaiseGurantee(models.Model):
    _name = 'guarantee.increase'
    _rec_name = 'number'
    _inherit = ["mail.thread"]


    number = fields.Char('Sequence')
    letter_guarantee_id = fields.Many2one(comodel_name='guarantee.letter',string="Gurantee Letter", domain=[('is_close', '=', False)])

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('confirm', 'Confirm'),
                                                        ], required=False, default="draft")
    
    partner_id = fields.Many2one(related='letter_guarantee_id.partner_id', string='Customer', comodel_name='res.partner')
    analytic_id = fields.Many2one(related='letter_guarantee_id.analytic_id',string= 'Expenses Analytic Account')
    
    journal_id = fields.Many2one(related='letter_guarantee_id.journal_id', string='Bank')
    letter_type = fields.Selection(string="Letter Type",related='letter_guarantee_id.letter_type')
    letter_amount = fields.Float('Letter Amount',related='letter_guarantee_id.letter_amount')
    bank_expense_account_id = fields.Many2one('account.account', string="Account Expenses Debit")

    transaction_date = fields.Date(string="Transaction Date",related='letter_guarantee_id.transaction_date' )
    start_date = fields.Date(string="Start Date",related='letter_guarantee_id.start_date' )
    end_date = fields.Date(string="End Date",related='letter_guarantee_id.end_date' )
    config_id = fields.Many2one(related='letter_guarantee_id.config_id', string='Letter Name')
    move_id = fields.Many2one('account.move', 'Letter Journal')
    expenses_id = fields.Many2one('account.move', 'Expenses Journal')
    cover_amount_percentage =fields.Float('Cover Percentage %')
    cover_amount =fields.Float('Cover Amount ')
    raise_amount = fields.Float('Raise Amount', )
    total_amount = fields.Float('Total Amount',compute='compute_total_amount' )
    is_expenses = fields.Boolean('Is Expense')
    expenses_amount = fields.Float('Expenses Amount', )
    note = fields.Text('Note')
    is_close=fields.Boolean('Is Closed',compute='compute_closed')


    @api.depends('letter_guarantee_id')
    def compute_closed(self):
        for rec in self:
            letter = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
            rec.is_close = all(l.is_close for l in letter)


    @api.depends('letter_amount',)
    def compute_total_amount(self):
        for rec in self:
            raise_guarantee = self.env['guarantee.increase'].search([('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
            x = 0.0
            for lin in raise_guarantee:
                x = x + lin.raise_amount
            # rec.raise_amount = x
            rec.total_amount = rec.letter_amount + x

    @api.onchange('cover_amount')
    def _onchange_cover_amount(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount_percentage = rec.cover_amount / rec.raise_amount * 100

    @api.onchange('cover_amount_percentage')
    def _onchange_cover_amount_percentage(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount = rec.raise_amount * rec.cover_amount_percentage / 100

    def cancel_button(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.button_cancel()
                rec.move_id.unlink()
                rec.state = 'draft'
            else:
                rec.state = 'draft'
            if rec.expenses_id:
                rec.expenses_id.button_cancel()
                rec.expenses_id.unlink()
                rec.state = 'draft'
            else:
                rec.state = 'draft'

    def confirm_button(self):
        for rec in self:
            config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,
                'date': rec.start_date,
            })
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,
                    'account_id': config.account_id.id,
                    'name': 'Raise Gurantee Letter',
                    'debit': rec.cover_amount,
                })
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,
                    'account_id': rec.journal_id.default_account_id.id,
                    'name': 'Gurantee Letter',
                    'credit': rec.cover_amount,
                })
            move.post()
            rec.move_id = move.id
            if rec.is_expenses :
                config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
                move = self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,
                    'date': rec.start_date,
                })
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,
                        'account_id': config.bank_expense_account_id.id,
                        'name': 'Expense Raise Gurantee',
                        'analytic_account_id': rec.analytic_id.id,
                        'debit': rec.expenses_amount,
                    })
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,
                        'account_id': rec.journal_id.default_account_id.id,
                        'name': 'Expense Raise Gurantee',
                        'analytic_account_id': rec.analytic_id.id,
                        'credit': rec.expenses_amount,
                    })
                move.post()
                rec.expenses_id = move.id
            rec.state = "confirm"

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('guarantee.increase') or '/'
        vals['number'] = seq
        return super(RaiseGurantee, self).create(vals)

