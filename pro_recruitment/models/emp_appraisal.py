from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError, UserError


class EmpAppraisal(models.Model):
    _name = "emp.appraisal"

    name = fields.Char('Name')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Manager', required=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, required=True)
    line_ids = fields.One2many(comodel_name='emp.appraisal.line', inverse_name='emp_appraisal_id')


class HrAppraisalSkill(models.Model):
    _name = "emp.appraisal.line"

    emp_appraisal_id = fields.Many2one('emp.appraisal')
    target_goal_id = fields.Many2one('target.goal', string='Objective', required=True)
    score = fields.Selection(string='Score', selection=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ], required=True)
