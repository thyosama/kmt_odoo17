# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    objective_ids = fields.One2many(comodel_name='hr.department.obj', inverse_name='department_id')
    goal = fields.Text('Firm Goal')


class HrDepartmentObj(models.Model):
    _name = 'hr.department.obj'

    department_id = fields.Many2one('hr.department')
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Name')
    description = fields.Text('Description')
