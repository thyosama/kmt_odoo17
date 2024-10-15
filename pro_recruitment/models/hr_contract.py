from odoo import _, api, exceptions, fields, models


class Contract(models.Model):
    _inherit = 'hr.contract'

    emp_job_id = fields.Many2one('emp.job.title', string='Job Position',
                                 related='employee_id.emp_job_title_id')


class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    emp_job_id = fields.Many2one('emp.job.title', string='Job Position', readonly=True,
                                 related='employee_id.emp_job_title_id')
