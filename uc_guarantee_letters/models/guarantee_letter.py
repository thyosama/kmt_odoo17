# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class LetterOfGurantee(models.Model):
    _name = 'guarantee.letter'
    _rec_name = 'letter_number'
    _inherit = ["mail.thread"]

    number = fields.Char('Sequence')
    state = fields.Selection(string="State", 
        selection=[
            ('draft', 'Draft'),('confirm', 'Confirm'),], 
        required=False, default="draft"
        )
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner',)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Bank',domain=[('type','=','bank')],)
    letter_type = fields.Selection(string="Letter Type",selection=[('premium', 'Premium'), ('final', 'Final'), ('deposit', 'Deposit'), ],)
    config_id = fields.Many2one('guarantee.letter.setting', 'Letter Name',)
    analytic_id = fields.Many2one('account.analytic.account', 'Expenses Analytic Account',)
    move_id = fields.Many2one('account.move', 'Letter Journal',)
    expenses_id = fields.Many2one('account.move', 'Expenses Journal',)
    letter_amount =fields.Float('Letter Amount',)
    cover_amount_percentage =fields.Float('Cover Percentage %',)
    cover_amount =fields.Float('Cover Amount ',)
    is_expenses = fields.Boolean('Is Expense',)
    is_letter_name = fields.Boolean('Is letter name',default=False,)
    expenses_amount = fields.Float('Expenses Amount',)
    transaction_date = fields.Date(string="Transaction Date",)
    start_date = fields.Date(string="Start Date",)
    end_date = fields.Date(string="End Date",)
    letter_number=fields.Char('Letter Number',)
    note=fields.Text('Note',)
    is_close=fields.Boolean('Is Closed',readonly=True)


    @api.onchange('letter_type')
    def _onchange_letter_name_readonly(self):
        if self.letter_type:
            self.is_letter_name = True

    @api.onchange('letter_type')
    def _onchange_letter_type(self):
        res = {}
        if self.letter_type:
            res['domain'] = {'config_id': [('letter_type', '=', self.letter_type)]}
        else:
            res['domain'] = {'config_id': []}
        return res

    @api.onchange('cover_amount')
    def _onchange_cover_amount(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount_percentage =rec.cover_amount/rec.letter_amount*100

    @api.onchange('cover_amount_percentage')
    def _onchange_cover_amount_percentage(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount = rec.letter_amount * rec.cover_amount_percentage /100
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and not rec.move_id:
                raise UserError('Can not delete')
            else:
                super().unlink()

    def cancel_button(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.button_cancel()
                rec.move_id.unlink()
                rec.state= 'draft'
            else:
                rec.state = 'draft'
            if rec.expenses_id:
                rec.expenses_id.button_cancel()
                rec.expenses_id.unlink()
                rec.state= 'draft'
            else:
                rec.state = 'draft'

    def confirm_button(self):
        for rec in self:
            config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,'date': rec.start_date,})
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,'account_id': config.account_id.id,'name': 'Gurantee Letter','debit': rec.cover_amount,})
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,'account_id': rec.journal_id.default_account_id.id,'name': 'Gurantee Letter','credit': rec.cover_amount,})
            move.post()
            rec.move_id = move.id
            if rec.is_expenses :
                config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
                move = self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,'date': rec.start_date,})
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,'account_id': config.bank_expense_account_id.id,'name': 'Gurantee Letter','analytic_account_id': rec.analytic_id.id,'debit': rec.expenses_amount,})

                # self.env['account.move.line'].with_context(check_move_validity=False).create(
                #     {
                #         'move_id': move.id, 'account_id': rec.journal_id.default_account_id.id,'analytic_account_id': rec.analytic_id.id,
                #         'name': 'Gurantee Letter', 'credit': rec.expenses_amount,
                #     })

                # remove analytic account from credit
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,'account_id': rec.journal_id.default_account_id.id,'name': 'Gurantee Letter',
                        'credit': rec.expenses_amount,
                    })
                move.post()
                rec.expenses_id = move.id
            rec.state = "confirm"


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('guarantee.letter') or '/'
        vals['number'] = seq
        return super(LetterOfGurantee, self).create(vals)

