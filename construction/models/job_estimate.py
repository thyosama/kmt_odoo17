from odoo.exceptions import ValidationError

from odoo import models, fields, api


class ConstructionJobEstimate(models.TransientModel):
    _name = "construction.job.estimate"
    indirect_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string="Indirect Type",
                                     default="percentage")
    profit_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string="Profit Type",
                                   default="percentage")
    indirect_percentage = fields.Float("Indirect Cost Percentage")
    indirect_amount = fields.Float("Indirect Cost Amount")
    tax_percentage = fields.Float("Tax Value Percentage")
    profit_percentage = fields.Float("Profit Percentage")
    profit_amount = fields.Float("Profit Amount")
    job_cost_ids = fields.Many2many("construction.job.cost", "job_id", "estimate_id")
    wiz_type = fields.Selection(
        string='Wiz_type',
        selection=[('indirect_type', 'indirect_type'),
                   ('profit_type', 'Profit Type'),
                   ('tax_percentage', 'Tax Percentage'),
                   ],
        required=False, )


    def create_estimation_cost(self):
        for rec in self.job_cost_ids:
            if self.indirect_type and self.wiz_type == 'indirect_type':
                rec.indirect_type = self.indirect_type
                if rec.indirect_type == 'percentage':
                    rec.indirect_percentage = self.indirect_percentage
                elif rec.indirect_type == 'amount':
                    rec.indirect_amount = self.indirect_amount
            if self.profit_type and self.wiz_type == 'profit_type':
                rec.profit_type = self.profit_type
                if rec.profit_type == 'amount':
                    rec.profit_amount = self.profit_amount
                elif rec.profit_type == 'percentage':
                    rec.profit_percentage = self.profit_percentage
            if self.tax_percentage>0  and self.wiz_type == 'tax_percentage':
                rec.tax_percentage = self.tax_percentage
            rec.state ='approve'
            rec.tender_id.state = 'job_estimate'
            rec.tender_id.price_unit = rec.sales_price

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

