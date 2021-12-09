from datetime import datetime

from odoo import models, fields, api


class wizard(models.TransientModel):
    _name = 'invoice.wizard'
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type", default='owner')
    contract_ids = fields.Many2many('construction.contract', 'contratct_ids', 'id', domain="[('type','=',type)]")

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def view_report(self):
        if self.type=='owner':
            view_form = self.env.ref('construction.view_account_invoice_tree_report_owner')
        else:
            view_form = self.env.ref('construction.view_account_invoice_tree_report_sup')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree',
            'views': [(view_form.id, 'tree')],
            'res_model': 'account.invoice',
            'domain': [('contract_id', 'in', self.contract_ids.ids)],
            'target': 'current',

        }
