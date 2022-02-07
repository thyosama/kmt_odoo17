# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SendGurantee(models.Model):
    _name = 'guarantee.recieve'

    type = fields.Selection(string="Type", selection=[('letter', 'Letter'),('cheque', 'Cheque'),  ],)
    state = fields.Selection(string="State", selection=[('recieve', 'Recieve'),('return', 'Return'),  ],)
    letter_guarantee_id = fields.Many2one(comodel_name='guarantee.letter', string="Gurantee Letter")
    
    partner_id = fields.Many2one(related='letter_guarantee_id.partner_id', string='Customer', comodel_name='res.partner')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    
    letter_number = fields.Char( string='Letter Number')
    bank_id = fields.Many2one('res.bank', string='Bank')
    letter_amount = fields.Float('Letter Amount', )

    transaction_date = fields.Date(string="Transaction Date", )
    start_date = fields.Date(string="Start Date", )
    due_date = fields.Date(string="Due Date", )
    end_date = fields.Date(string="End Date", )
    cheque_no = fields.Char('Cheque No')
    cheque_amount = fields.Char('Cheque Amount')
    note = fields.Text('Note')

