# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids


class attendnce_sheet(models.Model):
    _inherit = 'attendance.sheet'
    batch_id = fields.Many2one("attendance.sheet.batch")

    def action_attsheet_confirm(self):
        self.state = 'confirm'


class attendance_sheet_batch(models.Model):
    _name = 'attendance.sheet.batch'
    date_from = fields.Date(string="From", required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="To", required=True,
                          default=str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
    is_generate = fields.Boolean(copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved')], default='draft', track_visibility='onchange',
        string='Status', copy=False)
    name = fields.Char("Name", copy=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=False,
                                 default=lambda self: self.env.company.id)

    # att_policy_id = fields.Many2one(comodel_name='hr.attendance.policy', string="Attendance Policy ",)

    @api.constrains('date_from', 'date_to')
    def _get_period(self):
        if self.date_from > self.date_to:
            raise ValidationError("Date From must be less than Date to ")

    def generate_bacth(self):

        employee_ids = self.env['hr.employee'].search([])
        sheet_ids = self.env['attendance.sheet']
        for rec in employee_ids:
            att_policy_id = ''
            self.env['hr.payslip'].get_contract(rec, self.date_from, self.date_to)
            contract_ids = self.env['hr.payslip'].get_contract(rec, self.date_from, self.date_to)
            if contract_ids:
                contract_id = self.env['hr.contract'].browse(contract_ids[0])
                if contract_id.att_policy_id:
                    att_policy_id = contract_id.att_policy_id
                    sheet_ids = self.env['attendance.sheet'].create({
                        'company_id': self.company_id.id,
                        'employee_id': rec.id,
                        'date_from': self.date_from,
                        'date_to': self.date_to,
                        'accrual_date': self.date_to,
                        'att_policy_id': att_policy_id.id,
                        'batch_id': self.id
                    })
                    sheet_ids.get_attendances()
                    # sheet_ids.calculate_att_data()
                    sheet_ids.onchange_employee()
        self.is_generate = True

    def view_attendance_sheet(self):
        return {
            'name': ('Attendance Sheet'),
            'view_mode': 'tree,form',
            'res_model': 'attendance.sheet',
            'domain': [('batch_id', '=', self.id)],

            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_attsheet_confirm(self):

        sheet_id = self.env['attendance.sheet'].search([('batch_id', '=', self.id)])
        for rec in sheet_id:
            rec.action_attsheet_confirm()
        self.state = 'confirm'

    def action_attsheet_approve(self):

        sheet_id = self.env['attendance.sheet'].search([('batch_id', '=', self.id)])
        for rec in sheet_id:
            rec.action_approve()
        self.state = 'done'
