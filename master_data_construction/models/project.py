from odoo import fields, models, api
# from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = 'project.project'
    date_from = fields.Date("Project Begining", tracking=True)
    date_to = fields.Date("Project End Date", tracking=True)
    project_number = fields.Char(compute='get_project_number', tracking=True)
    created_date = fields.Date("Created Date", default=datetime.today(), tracking=True)
    consultant = fields.Many2one("res.partner", string="Consultant", tracking=True)
    manager_id = fields.Many2one("res.partner", string="Manager", tracking=True)
    project_reference = fields.Char(tracking=True)
    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())
    analytic_account = fields.Many2one("account.analytic.account")
    currancy_ids = fields.One2many("project.currency", "project_id")
    partner_id = fields.Many2one("res.partner",required=True)
    percentage = fields.Float("نسبه الانجاز")
    profit_indirect = fields.Boolean("Profit / indirect")
    def update_ratio_currancy(self):
        job_ids = self.env['construction.job.cost'].search([('techical_type','=',False),('state','!=','quotation'),('project_id', '=', self.id)])

        for record in job_ids:
            for rec in record.material_ids:
                currancy_id = self.env['project.currency'] \
                    .search([('currancy_id', '=', rec.currancy_id.id), ('project_id', '=', self.id)])

                if currancy_id:
                    rec.ratio = currancy_id.ratio
                if record.state != 'quotation':
                    rec._compute_sub_total()
                    record._compute_all_values()
                    record.compute_total_with_qty()
            if record.tender_id and record.state in( 'quotation','approve'):
                record.tender_id.price_unit = record.total_value_all
                # record.tender_id.calculate_sales_price()
                # record.tender_id._get_total_value()

                    # record.action_approve()
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id
    @api.depends('name')
    def get_project_number(self):
        for rec in self:
            rec.project_number = ''
            if rec.id:
                rec.project_number = "PR/" + str(rec.id).zfill(5)

    def duplicte_job_cost(self, new_job_id, old_job_id):
        for rec in old_job_id.material_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            new_line._compute_total_qty()
            new_line._compute_total_value()

        for rec in old_job_id.labour_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            new_line._compute_total_qty()
            new_line._compute_total_value()

        for rec in old_job_id.expense_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            new_line._compute_total_qty()
            new_line._compute_total_value()

        for rec in old_job_id.subconstractor_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            new_line._compute_total_qty()
            new_line._compute_total_value()

        for rec in old_job_id.equipment_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            new_line._compute_total_qty()
            new_line._compute_total_value()