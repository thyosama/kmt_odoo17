from odoo import fields, models, api


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    type = fields.Selection( string='Type', selection=[
        ('partner', 'Partner'),  ('employee', 'Employee'),  ('manager', 'Manager')], required=True)
    emp_id = fields.Many2one(comodel_name='res.users', string="Employee", required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    applicant_name = fields.Char(string="Applicant Name", compute="compute_applicant_name")

    @api.depends('applicant_id')
    def compute_applicant_name(self):
        for rec in self:
            rec.applicant_name = False
            if rec.applicant_id:
                rec.applicant_name = rec.applicant_id[0].partner_name

