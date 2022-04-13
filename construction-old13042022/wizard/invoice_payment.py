from odoo import fields, models, api


class ConstructionPaymentWizard(models.TransientModel):
    _name = 'construction.payment.wizard'

    payment_ids = fields.Many2many('account.payment', string="Payment")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Customer")
    contract_id = fields.Many2one("construction.contract", string="Contract")
    project_id = fields.Many2one('project.project', string="Project",)

    def confirm(self):
        for line in self.payment_ids:
            line.invoice_ids = self.invoice_id.id
            line.contract_id = self.contract_id.id
            line.project_id = self.project_id.id
            # line.action_post()

    @api.onchange('partner_id')
    def change_partner_id(self):
        for rec in self:
            payment_ids = self.env['account.payment'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('payment_type', '=', 'outbound'),
                ('partner_type', '=', 'supplier'),
                ('invoice_ids', '=', False),
                ('state', '=', 'posted'),
            ])
            return {'domain': {'payment_ids': [('id', 'in', payment_ids.ids)]}}
