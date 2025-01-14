# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2020-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api, tools, _
import babel
import time
from datetime import datetime, timedelta
from pytz import timezone


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    att_policy_id = fields.Many2one('hr.attendance.policy',
                                    string='Attendance Policy')



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_expected_attendances(self, date_from, date_to):
        self.ensure_one()
        employee_timezone = timezone(self.tz) if self.tz else None
        calendar = self.resource_calendar_id or self.company_id.resource_calendar_id
        calendar_intervals = calendar._work_intervals_batch(
                                date_from,
                                date_to,
                                tz=employee_timezone,
                                resources=self.resource_id,
                                compute_leaves=True,
                                domain=[('company_id', 'in', [False, self.company_id.id])])[self.resource_id.id]
        return calendar_intervals
