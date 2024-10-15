from odoo import fields, models, api


class EMPJobTitle(models.Model):
    _name = 'emp.job.title'
    _description = 'name'

    name = fields.Char(required=True)
    job_description = fields.Html('Job Description')
    job_specification = fields.Html('Job Specification')
    target_ratio = fields.Float('Target Ratio')
    competencies_ratio = fields.Float('Competencies Ratio')
    max_bonuce = fields.Float('Max Bonus')
    skill_rate_ids = fields.One2many(comodel_name='hr.skill.rate', inverse_name='emp_job_title_id')
