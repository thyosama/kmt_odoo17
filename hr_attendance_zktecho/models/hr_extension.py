# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrAttendance(models.Model):
    
    _inherit = 'hr.attendance'
    
    name = fields.Datetime('Datetime')
    day = fields.Date("Day")
    is_missing = fields.Boolean('Missing', default=False)


class hrDraftAttendance(models.Model):

    _name = 'hr.draft.attendance'
    _inherit = ['mail.thread']
    _order = 'name desc'
    
    name = fields.Datetime('Datetime', required=False)
    date = fields.Date('Date', required=False)
    day_name = fields.Char('Day')
    attendance_status = fields.Selection([('sign_in', 'Sign In'), \
                                          ('sign_out', 'Sign Out'), ('sign_none', 'None')],\
                                         'Attendance State', required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    lock_attendance = fields.Boolean('Lock Attendance')
    biometric_attendance_id = fields.Integer(string='Biometric Attendance ID')
    is_missing = fields.Boolean('Missing', default=False)

    # @api.depends('employee_id','name')
    # def _get_sign_state(self):
    #     for rec in self:
    #         check_attend = self.env['hr.draft.attendance'].search(
    #             [('employee_id', '=', rec.employee_id.id), ('date', '=', rec.date), ],
    #             order='name asc')
    #         check_attend_out = self.env['hr.draft.attendance'].search(
    #             [('employee_id', '=', rec.employee_id.id), ('date', '=', rec.date), ],
    #             order='name desc')
    #         rec.attendance_status='sign_none'
    #         if check_attend.name == rec.name and len(check_attend) == 1:
    #             rec.attendance_status='sign_in'
    #         if check_attend_out.name == rec.name and len(check_attend_out) == 1:
    #             rec.attendance_status='sign_out'


class Employee(models.Model):
    
    _inherit = 'hr.employee'
    
    is_shift = fields.Boolean("Shifted Employee")
    attendance_devices = fields.One2many(comodel_name='employee.attendance.devices', inverse_name='name', string='Attendance')
    old_branch = fields.Char()


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    is_shift = fields.Boolean("Shifted Employee")
    attendance_devices = fields.One2many(comodel_name='employee.attendance.devices', inverse_name='emp_public', string='Attendance')
    old_branch = fields.Char()
    no_attendance = fields.Boolean(string="Exempt from Attendance", help="This checkbox defines whether the employee's payslip is related to their attendance or not")


class EmployeeAttendanceDevices(models.Model):
    
    _name = 'employee.attendance.devices'
    
    name = fields.Many2one(comodel_name='hr.employee', string='Employee')
    emp_public = fields.Many2one(comodel_name='hr.employee.public', string='Employee')
    attendance_id = fields.Char("Attendance ID", required=True)
    device_id = fields.Many2one(comodel_name='biomteric.device.info', string='Biometric Device', required=True, ondelete='restrict')
    
    # @api.one
    @api.constrains('attendance_id', 'device_id', 'name')
    def _check_unique_constraint(self):
        for rec in self:
            # self.ensure_one()
            record = self.search([
                ('attendance_id', '=', rec.attendance_id),
                ('device_id', '=', rec.device_id.id),
                ('id', '!=', rec.id)
            ], limit=1)
            if len(record) >= 1:
                raise ValidationError('Employee with Id ('+ str(rec.attendance_id)+') exists on Device ('+ str(rec.device_id.name)+') !'+ 'for EMP '+str(record.name))
            record = self.search([('name', '=', rec.name.id), ('device_id', '=', rec.device_id.id)])
            if len(record) > 1:
                raise ValidationError('Configuration for Device ('+ str(rec.device_id.name)+') of Employee  ('+ str(rec.name.name)+') already exists!')
