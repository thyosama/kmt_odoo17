# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrAttendancePolicy(models.Model):
    _inherit = 'hr.attendance.policy'

    miss_rule_id = fields.Many2one(comodel_name="hr.miss.rule",
                                   string="Missed Punch Rule", required=False)
    # ,job_id
    def get_late(self,period, cnt):
        res = period
        flag = False
        no = 1
        cnt_flag = False
        factor = 1
        if period <= 0:
            return 0, cnt
        if self.late_rule_id:
            time_ids = self.late_rule_id.line_ids.sorted(key=lambda r: r.time, reverse=True)
            for line in time_ids:
                # and line.job_id.id==job_id
                print(period, " 99999999 ", line.time)
                if (period >= line.time) :
                    print("Leeeeeeeeeeeees")
                    for counter in cnt:
                        if counter[0] == line.time:
                            cnt_flag = True
                            no = counter[1]
                            counter[1] += 1
                            break
                    if no >= 5 and line.fifth > 0:
                        factor = line.fifth
                    elif no >= 4 and line.fourth > 0:
                        factor = line.fourth
                    elif no >= 3 and line.third > 0:
                        factor = line.third
                    elif no >= 2 and line.second > 0:
                        factor = line.second
                    elif no >= 1 and line.first > 0:
                        factor = line.first
                    elif no == 0:
                        factor = 0
                    if not cnt_flag:
                        cnt.append([line.time, 2])
                    flag = True
                    print(">>>>>>>>Line<<<<<<<<< ",line.type)
                    if line.type == 'rate':
                        res = line.rate * period * factor
                        print("Rate: ", line.rate, "Period: ", period, "Factor:", factor)
                    elif line.type == 'fix':
                        res = line.amount * factor
                    elif line.type == 'percentage':
                        res = line.percentage * factor
                        print("Obiedddddddddddddddddd", res)
                    break
            if not flag:
                res = 0
        print(res, "--------- ", cnt)
        return res, cnt
    # ,job_id
    def get_diff(self, period, diff_cnt):
        res = period
        flag = False
        no = 1
        cnt_flag = False
        factor = 1
        if period <= 0:
            return 0, diff_cnt
        if self.diff_rule_id:
            time_ids = self.diff_rule_id.line_ids.sorted(
                key=lambda r: r.time, reverse=True)
            for line in time_ids:
                # and line.job_id.id==job_id
                if (period >= line.time) :
                    for counter in diff_cnt:
                        if counter[0] == line.time:
                            cnt_flag = True
                            no = counter[1]
                            counter[1] += 1
                            break
                    if no >= 5:
                        factor = line.fifth
                    elif no >= 4:
                        factor = line.fourth
                    elif no >= 3:
                        factor = line.third
                    elif no >= 2:
                        factor = line.second
                    elif no >= 1:
                        factor = line.first
                    elif no >= 0:
                        factor = 1
                    if not cnt_flag:
                        diff_cnt.append([line.time, 2])
                    flag = True
                    if line.type == 'rate':
                        res = line.rate * period * factor
                    elif line.type == 'fix':
                        res = line.amount * factor
                    elif line.type == 'percentage':
                        res = line.percentage * factor
                    break
            if not flag:
                res = 0
        return res, diff_cnt
    # ,job_id
    def get_miss(self, cnt):
        self.ensure_one()
        res = 0
        flag = False
        if self:
            if self.miss_rule_id:
                miss_ids = self.miss_rule_id.line_ids.sorted(
                    key=lambda r: r.counter, reverse=True)
                for ln in miss_ids:
                    # and ln.job_id.id==job_id
                    if (cnt >= int(ln.counter)) :
                        res = ln.amount
                        flag = True
                        break
                if not flag:
                    res = 0
        return res

class HrLateRuleLine(models.Model):
    _inherit = 'hr.late.rule.line'

    first = fields.Float('First Time', default=1)
    second = fields.Float('Second Time', default=1)
    third = fields.Float('Third Time', default=1)
    fourth = fields.Float('Fourth Time', default=1)
    fifth = fields.Float('Fifth Time', default=1)


class HrDiffRuleLine(models.Model):
    _inherit = 'hr.diff.rule.line'

    first = fields.Float('First Time', default=1)
    second = fields.Float('Second Time', default=1)
    third = fields.Float('Third Time', default=1)
    fourth = fields.Float('Fourth Time', default=1)
    fifth = fields.Float('Fifth Time', default=1)

class hr_miss_rule(models.Model):
    _name = 'hr.miss.rule'

    name = fields.Char(string='name', required=True,translate=True)
    line_ids = fields.One2many(comodel_name='hr.miss.rule.line', inverse_name='miss_id', string='Missed punchis rules')


class hr_miss_rule_line(models.Model):
    _name = 'hr.miss.rule.line'

    times = [
        ('1', 'First Time'),
        ('2', 'Second Time'),
        ('3', 'Third Time'),
        ('4', 'Fourth Time'),
        ('5', 'Fifth Time'),

    ]

    miss_id = fields.Many2one(comodel_name='hr.miss.rule', string='name')
    amount = fields.Float(string='amount',required=True)
    counter = fields.Selection(string="Times", selection=times, required=True, )
    job_id = fields.Many2one(comodel_name="hr.job", string="Job", required=False)

    _sql_constraints = [
        ('miss_rule_cons', 'unique(miss_id,counter)',
         'The counter Must Be unique Per Rule'),
    ]






