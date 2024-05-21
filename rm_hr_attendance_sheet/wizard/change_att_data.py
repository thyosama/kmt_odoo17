import time
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp







class attendance_sheet_line_change(models.TransientModel):
    _name = "attendance.sheet.line.change"
    overtime = fields.Float("Overtime")
    late_in = fields.Float("Late In")
    diff_time = fields.Float("Diff Time")
    note = fields.Text("Note",required=True)
    att_line_id=fields.Many2one(comodel_name="attendance.sheet.line")

    @api.model
    def default_get(self, fields):
        res = super(attendance_sheet_line_change, self).default_get(fields)
        atts_line_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        if 'overtime' in fields and 'overtime' not in res:
            res['overtime'] = atts_line_id.act_overtime
            res['late_in'] = atts_line_id.act_late_in
            res['diff_time'] = atts_line_id.act_diff_time
            res['att_line_id'] = atts_line_id.id
        return res

    def get_late_time(self, xline):
        no = 0
        late_rules = {}
        factor = 1
        for xln in xline:
            if xln.att_sheet_id.att_policy_id.late_rule_id:
                time_ids = xln.att_sheet_id.att_policy_id.late_rule_id.line_ids.sorted(key=lambda r: r.time, reverse=True)
                if time_ids.filtered(lambda l: xln.act_late_in > l.time):
                    for line in time_ids.filtered(lambda l: xln.act_late_in > l.time)[0]:
                        if line.time in late_rules:
                            pass
                        else:
                            late_rules.update({line.time : 0})
                        if (xln.act_late_in >= line.time):
                            if xln.pro_status_id and xln.act_late_in>0:
                                if xln.pro_status_id.type == 'calc':
                                    pass
                                else:
                                    if xln.act_late_in > 0:
                                        if line.time in late_rules:
                                            late_rules[line.time] += 1
                                            no = late_rules[line.time]
                            else:
                                if xln.act_late_in > 0:
                                    if line.time in late_rules:
                                        late_rules[line.time] += 1
                                        no = late_rules[line.time]
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
                            if line.type == 'rate':
                                xln.late_in = line.rate * xln.act_late_in * factor
                            elif line.type == 'fix':
                                xln.late_in = line.amount * factor
                            elif line.type == 'percentage':
                                xln.late_in = line.percentage * factor
                            if xln.pro_status_id and xln.act_late_in>0:
                                if xln.pro_status_id.type == 'calc':
                                    xln.late_in = 0

    def get_ovt_time(self, line):
        line.overtime = 0
        if not line.status:
            rule_ids = line.att_sheet_id.att_policy_id.overtime_rule_ids.filtered(lambda r: r.type == 'workday' and line.act_overtime > r.active_after)
            early_rule_ids = line.att_sheet_id.att_policy_id.overtime_rule_ids.filtered(lambda r: r.type == 'workday' and (line.pl_sign_in - line.ac_sign_in) > r.active_after)

        else:
            rule_ids = line.att_sheet_id.att_policy_id.overtime_rule_ids.filtered(lambda r: r.type == 'weekend')
            early_rule_ids = line.att_sheet_id.att_policy_id.overtime_rule_ids.filtered(lambda r: r.type == 'weekend' and (line.pl_sign_in - line.ac_sign_in) > r.active_after)
        if rule_ids:
            line.overtime += (rule_ids[0].rate * line.act_overtime)
        if early_rule_ids:
            line.overtime += ((early_rule_ids[0].rate * (line.pl_sign_in - line.ac_sign_in) if early_rule_ids[0].rate * (line.pl_sign_in - line.ac_sign_in) > 0 else 0)) if early_rule_ids and line.pro_status_id and  line.ac_sign_in >0 else 0

    def get_absence_time(self, line):
        for rec in self:
            cnt = 1
            if line.status == 'ab':
                abs_ids = line.att_sheet_id.att_policy_id.absence_rule_id.line_ids.sorted(key=lambda r: r.counter, reverse=True)
                print(abs_ids)
                for ln in abs_ids:
                    if line.pro_status_id.type != 'calc':
                        if (cnt >= int(ln.counter)):
                            print("XXXXXXXXXXXXX nnnnnnnnn ",ln.rate)
                            line.diff_time= ln.rate * line.act_diff_time
                            cnt +=1
                            break
            count = 1
            if line.status != 'ab' and line.act_diff_time > 0:
                no = 0
                late_rules = {}
                factor = 1
                for xln in line:
                    if xln.att_sheet_id.att_policy_id.diff_rule_id:
                        time_ids = xln.att_sheet_id.att_policy_id.diff_rule_id.line_ids.sorted(key=lambda r: r.time,
                                                                                               reverse=True)
                        if time_ids.filtered(lambda l: xln.act_diff_time > l.time):
                            for line in time_ids.filtered(lambda l: xln.act_diff_time > l.time)[0]:
                                if line.time in late_rules:
                                    pass
                                else:
                                    late_rules.update({line.time: 0})
                                if (xln.act_diff_time >= line.time):
                                    if xln.pro_status_id and xln.act_diff_time > 0:
                                        if xln.pro_status_id.type == 'calc':
                                            pass
                                        else:
                                            if xln.act_diff_time > 0:
                                                if line.time in late_rules:
                                                    late_rules[line.time] += 1
                                                    no = late_rules[line.time]
                                    else:
                                        if xln.act_diff_time > 0:
                                            if line.time in late_rules:
                                                late_rules[line.time] += 1
                                                no = late_rules[line.time]
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
                                    if line.type == 'rate':
                                        xln.diff_time = line.rate * xln.act_diff_time * factor
                                    elif line.type == 'fix':
                                        xln.diff_time = line.amount * factor
                                    elif line.type == 'percentage':
                                        xln.diff_time = line.percentage * factor
                                    if xln.pro_status_id and xln.act_diff_time > 0:
                                        if xln.pro_status_id.type == 'calc':
                                            xln.diff_time = 0

    def change_att_data(self):
        [data]=self.read()
        self.ensure_one()
        atts_line_id = self.env['attendance.sheet.line'].browse(self._context['active_id'])
        res={
            'act_overtime':data['overtime'],
            'act_late_in':data['late_in'],
            'act_diff_time':data['diff_time'],
            'note': data['note'],
        }
        atts_line_id.write(res)
        self.get_ovt_time(atts_line_id)
        self.get_late_time(atts_line_id)
        self.get_absence_time(atts_line_id)
        # atts_line_id.att_sheet_id.calculate_att_data()
        return {'type': 'ir.actions.act_window_close'}

    #ToDo: this commented function was written by eng RAMDAN KHLIL commented by Abdurlhman As task  (#2444) in helpdesk
    # @api.model
    # def default_get(self, fields):
    #     res = super(attendance_sheet_line_change, self).default_get(fields)
    #     atts_line_id = self.env[self._context['active_model']].browse(self._context['active_id'])
    #     if 'overtime' in fields and 'overtime' not in res:
    #         res['overtime'] = atts_line_id.overtime
    #         res['late_in'] = atts_line_id.late_in
    #         res['diff_time'] = atts_line_id.diff_time
    #         res['att_line_id'] = atts_line_id.id
    #     return res
    # def change_att_data(self):
    #     [data]=self.read()
    #     self.ensure_one()
    #     atts_line_id = self.env['attendance.sheet.line'].browse(self._context['active_id'])
    #     res={
    #         'overtime':data['overtime'],
    #         'late_in':data['late_in'],
    #         'diff_time':data['diff_time'],
    #         'note': data['note'],
    #
    #     }
    #     atts_line_id.write(res)
    #     # atts_line_id.att_sheet_id.calculate_att_data()
    #     return {'type': 'ir.actions.act_window_close'}
