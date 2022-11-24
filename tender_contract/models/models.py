# -*- coding: utf-8 -*-

from odoo import models, fields, api
class Engineerlines(models.Model):
    _inherit = 'construction.engineer.lines'

    tender_id = fields.Many2one('construction.tender', string="Tender ID")
    # item = fields.Many2one(rela/ted='tender_id.item', string='Item')

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    tender_id = fields.Many2one('construction.tender', string="Tender ID")

    @api.onchange('tender_id')
    def change_tender_id(self):
        self.name = self.tender_id.name
        if self.invoice_id.contract_id:
            if self.invoice_id.contract_id.project_id:
                return {
                    'domain': {'tender_id': [('project_id', '=', self.invoice_id.contract_id.project_id.id)]}
                }
class subconstractor(models.Model):
    _inherit = 'construction.subconstractor'
    tender_id = fields.Many2one('construction.tender', string="Tender ID")
# class Job_estimation(models.Model):
#     _inherit = 'construction.job.cost'
#     tender_id = fields.Many2one("construction.tender")
#     def action_approve(self):
#         self.state = 'approve'
#         self.tender_id.state = 'job_estimate'
#         if self.techical_type==False:
#             self.tender_id.price_unit = self.total_value_all
#         # self.tender_id.total_value = self.total_value_all_with_q



# class tender_contract(models.Model):
#     _name = 'tender_contract.tender_contract'
#     _description = 'tender_contract.tender_contract'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
