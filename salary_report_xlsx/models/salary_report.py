# -*- coding: utf-8 -*-
from builtins import print
# import pandas as pd
# import pdfkit

from odoo import api, fields, models, tools, _
import xlsxwriter
import io  #
import base64
from odoo.exceptions import ValidationError, UserError


class ReportPayslips(models.TransientModel):
    _name = 'hr.payslip.salary.excel'

    start_date = fields.Date(string="Start Date", required=True, )
    end_date = fields.Date(string="End Date", required=True, )
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    struct_ids = fields.Many2many('hr.payroll.structure', string='Structure')
    hr_salary_rule_ids = fields.Many2many('hr.salary.rule', string='Salary Rules')
    excel_sheet = fields.Binary()
    company_id = fields.Many2one('res.company', string='company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done '),
        ('cancel', 'Cancelled'),
        ('paid', 'Paid'),
    ], string='Status', default='draft',)

    @api.onchange('struct_ids')
    def onchange_struct_ids(self):
        res = {}
        rules_ids = self.env['hr.salary.rule'].search([
            ('struct_id', 'in', self.struct_ids.ids),
            ('appears_on_payslip', '=', True)
        ])
        if len(rules_ids.ids) > 0:
            res['domain'] = {'hr_salary_rule_ids': [('id', 'in', rules_ids.ids)]}
        else:
            res['domain'] = {'hr_salary_rule_ids': [('id', '=', False)]}
        return res

    def print_report_excel(self):
        return self.env.ref('salary_report_xlsx.salary_report_xlsx').report_action(self)

    def print_pdf_report(self):
        employee_ids = self.employee_ids.ids  if self.employee_ids else self.env['hr.employee'].search([]).ids
        struct_ids = self.struct_ids.ids  if self.struct_ids else self.env['hr.payroll.structure'].search([]).ids
        hr_salary_rule_ids = self.hr_salary_rule_ids.ids  if self.hr_salary_rule_ids else self.env['hr.salary.rule'].search([]).ids
        print(">>>>>>>>xcxcx<<<<<<", self.hr_salary_rule_ids.ids)
        print(">>>>>>>>xcxcx<<<<<<", self.env['hr.salary.rule'].search([]).ids)
        hr_payslip_ids = self.env['hr.payslip'].search([
            ('employee_id', 'in', employee_ids),
            ('struct_id', 'in', struct_ids),
            ('date_from', '>=', self.start_date),
            ('date_to', '<=', self.end_date),
            ('state', '=', self.state),
        ])

        # self.generate_xlsx_report(workbook, hr_payslip_ids)
        data = {
            'model': self,
            'ids': self.ids,
            'model': self._name,
            'report_name': 'dddd',
            'form': {
                'date_from': self.start_date,
                'date_to': self.end_date,
                'hr_payslip_ids': hr_payslip_ids.ids,
                'struct_ids': struct_ids,
                'employee_ids': employee_ids,
                'hr_salary_rule_ids': hr_salary_rule_ids,
                'company_id': self.company_id.id,
            },
        }
        if len(hr_payslip_ids.ids) > 0:
            # return {'type': 'ir.actions.client', 'report_name': 'salary_report_xlsx.payslip_salary', 'datas': data}
            return self.env.ref('salary_report_xlsx.salary_report_xlsx_pdf').report_action([], data=data)

        else:
            raise ValidationError(' There is No Data to Show')

    def print_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        employee_ids = self.employee_ids.ids  if self.employee_ids else self.env['hr.employee'].search([]).ids
        struct_ids = self.struct_ids.ids  if self.struct_ids else self.env['hr.payroll.structure'].search([]).ids
        hr_salary_rule_ids = self.hr_salary_rule_ids.ids  if self.hr_salary_rule_ids else self.env['hr.salary.rule'].search([]).ids
        print(">>>>>>>>>>>>>>>>>>>>>>>>>", hr_salary_rule_ids)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>", self.env['hr.salary.rule'].search([]).ids)

        hr_payslip_ids = self.env['hr.payslip'].search([
            ('employee_id', 'in', employee_ids),
            ('struct_id', 'in', struct_ids),
            ('date_from', '>=', self.start_date),
            ('date_to', '<=', self.end_date),
            ('state', '=', self.state),
        ])

        # self.generate_xlsx_report(workbook, hr_payslip_ids)
        data = {
            'ids': self.ids,
            'model': self._name,
            'report_name': 'dddd',
            'form': {
                'date_from': self.start_date,
                'date_to': self.end_date,
                'hr_payslip_ids': hr_payslip_ids.ids,
                'struct_ids': struct_ids,
                'employee_ids': employee_ids,
                'hr_salary_rule_ids': hr_salary_rule_ids,
                'company_id': self.company_id.id,
            },
        }
        if len(hr_payslip_ids.ids) > 0:
            return self.env.ref('salary_report_xlsx.salary_report_xlsx2').report_action(self, data=data, )
        else:
            raise ValidationError(' There is No Data to Show')


    def generate_xlsx_report(self, workbook, data, lines):
        lines = self.env['hr.payslip'].browse(data["form"]['hr_payslip_ids'])
        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 12,
            'fg_color': 'white',
        })
        first_header = workbook.add_format({
            'bold': 0,
            'border': 2,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 15,
            'fg_color': '#A3C7F3'
        })
        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 12,
            'valign': 'vcenter',
            'fg_color': '#ededed'
        })

        worksheet = workbook.add_worksheet('hr payslip excel')
        worksheet.right_to_left()
        worksheet.set_column(0, 1, 20)
        worksheet.set_column(2, 3, 40)
        worksheet.set_column(4, 5, 20)
        worksheet.set_paper(9)
        worksheet.set_portrait()

        salary_rule_ids =  self.env['hr.salary.rule'].browse(data['form']['hr_salary_rule_ids']) if  len(data['form']['hr_salary_rule_ids'])>0 else self.env['hr.salary.rule'].search([], order='sequence asc')
        print(">>>salary<<<<, ",self.env['hr.salary.rule'].browse(data['form']['hr_salary_rule_ids']))
        print(">>>salary<<<<, ",self.env['hr.salary.rule'].search([], order='sequence asc'))
        total_dict = {}
        datas = []
        company_id = self.env['res.company'].browse(data['form']['company_id'])
        buf_image = io.BytesIO(base64.b64decode(company_id.logo))
        worksheet.insert_image(0, 4, 'img.png', {'image_data': buf_image, 'x_scale': 0.15, 'y_scale': 0.15})

        if salary_rule_ids:
            row = 4
            print(str(lines))
            print(str(lines))
            text = 'Employee Salary from Date' + str(lines[0].date_from) + "To" + str(lines[0].date_to)
            worksheet.merge_range('A3:C3', text, table_header_format)
            worksheet.write(2, 0, text, table_header_format)
            col = 0
            for rule in salary_rule_ids:
                worksheet.write(row, col, rule.name, table_header_format)
                total_dict.update({rule.id: 0})
            row += 1
            col = 2
            for slip in lines:
                line = {}
                row += 1
                for slip_line in slip.line_ids:
                    if slip_line.salary_rule_id.id in salary_rule_ids.ids:
                        line['ref'] = slip.number
                        line['code'] = slip.employee_id.pin if slip.employee_id.pin else ""
                        line['slip_name'] = slip.name
                        line['emp_name'] = slip.employee_id.name
                        line['bank_account_id'] = slip.employee_id.bank_account_id.acc_number if slip.employee_id.bank_account_id else ""
                        line['name'] = slip.employee_id.name
                        line['job'] = slip.employee_id.job_title
                        line['start_work'] = slip.employee_id.contract_id.date_start if slip.employee_id.contract_id else ""
                        line['department'] = slip.employee_id.contract_id.department_id.name if slip.employee_id.contract_id else ""
                        if slip_line.amount > 0:
                            line[slip_line.salary_rule_id.id] = slip_line.amount
                            total_dict.update(
                                {slip_line.salary_rule_id.id: total_dict[
                                                                  slip_line.salary_rule_id.id] + slip_line.amount})
                datas.append(line)
            row += 1
            col = 2
            row = 4

            rules_ids = []
            for rl in total_dict:
                if total_dict[rl] > 0:
                    rules_ids.append(rl)
            sal_rule_ids = self.env['hr.salary.rule'].search([('id', 'in', rules_ids)], order='sequence asc')
            col = 0
            worksheet.write(row, col, "#", table_header_format)
            col += 1
            worksheet.write(row, col, "Ref", table_header_format)
            col += 1
            worksheet.write(row, col, "Code", table_header_format)
            col += 1
            worksheet.write(row, col, "Name", table_header_format)
            col += 1
            worksheet.write(row, col, "Job", table_header_format)
            col += 1
            worksheet.write(row, col, "Work Date", table_header_format)
            col += 1
            worksheet.write(row, col, "Department", table_header_format)
            col += 1
            # Header Line
            for sa_line in sal_rule_ids:
                worksheet.write(row, col, sa_line.name, table_header_format)
                col += 1
            # worksheet.write(row, col, "Bank NO", table_header_format)
            # col += 1
            row += 1
            ############  Report Lines  ###############
            count = 0
            for line in datas:
                col = 0
                count += 1
                worksheet.write(row, col, count, custom_format)
                col += 1
                worksheet.write(row, col, line['ref'], custom_format)
                col += 1
                worksheet.write(row, col, line['code'], custom_format)
                col += 1
                worksheet.write(row, col, line['name'], custom_format)
                col += 1
                worksheet.write(row, col, line['job'], custom_format)
                col += 1
                worksheet.write(row, col, str(line['start_work']), custom_format)
                col += 1
                worksheet.write(row, col, line['department'], custom_format)
                col += 1
                for sa_line in sal_rule_ids:
                    if sa_line.id in line.keys():
                        worksheet.write(row, col, line[sa_line.id], custom_format)
                    col += 1
                # worksheet.write(row, col, line['bank_account_id'], custom_format)
                # col += 1
                row += 1
            col = 7
            for sa_line in sal_rule_ids:
                for tot in total_dict:
                    if tot == sa_line.id:
                        worksheet.write(row, col, total_dict[tot], table_header_format)
                col += 1
            col += 1
            row += 1

        else:
            raise ValidationError(_('There is no Salary Rules !!'))

    def formate_data_to_pdf(self, hr_payslip_ids, salary_rule_ids):
        lines = self.env['hr.payslip'].browse(hr_payslip_ids)
        salary_rule_ids =  self.env['hr.salary.rule'].browse(salary_rule_ids) if  len(salary_rule_ids)>0 else self.env['hr.salary.rule'].search([], order='sequence asc')
        print("RRRRRRRRRRRRRRRRRRRRRrr",salary_rule_ids)
        total_dict = {}
        datas = []

        if salary_rule_ids:
            for rule in salary_rule_ids:
                total_dict.update({rule.id: 0})
            for slip in lines:
                line = {}
                for slip_line in slip.line_ids:
                    print(slip_line.salary_rule_id.id)
                    if slip_line.salary_rule_id.id in salary_rule_ids.ids:
                        if slip_line.salary_rule_id.id == 15:
                            print(slip_line.salary_rule_id.name, '  1111 ', slip_line.amount)
                        line['ref'] = slip.number
                        line['code'] = slip.employee_id.pin if slip.employee_id.pin else ""
                        line['slip_name'] = slip.name
                        line['emp_name'] = slip.employee_id.name
                        line['bank_account_id'] = slip.employee_id.bank_account_id.acc_number if slip.employee_id.bank_account_id else ""
                        line['name'] = slip.employee_id.name
                        line['job'] = slip.employee_id.job_title
                        line['start_work'] = slip.employee_id.contract_id.date_start if slip.employee_id.contract_id else ""
                        line['department'] = slip.employee_id.contract_id.department_id.name if slip.employee_id.contract_id else ""
                        if slip_line.amount != 0:
                            line[slip_line.salary_rule_id.id] = slip_line.amount
                            print(">>>>>>line<<", line)
                            total_dict.update({slip_line.salary_rule_id.id: total_dict[slip_line.salary_rule_id.id] + slip_line.amount})
                datas.append(line)
            rules_ids = []
            for rl in total_dict:
                if total_dict[rl] != 0:
                    rules_ids.append(rl)
            sal_rule_ids = self.env['hr.salary.rule'].search([('id', 'in', rules_ids)], order='sequence asc')

            count = 0
            for line in datas:
                col = 0
                count += 1
                for sa_line in sal_rule_ids:
                    if sa_line.id in line.keys():
                        pass
                        # Salary rule name
            for sa_line in sal_rule_ids:
                for tot in total_dict:
                    if tot == sa_line.id:
                        pass
                        # in XML
        print("finalllllllll ",rules_ids)
        return {
            'rules_ids':rules_ids,
            'all_data':datas,
            'total_dict':total_dict,
        }



class SalaryReportXlsx(models.TransientModel):
    _name = 'report.salary_report_xlsx.payslip_salary'
    _inherit = 'report.report_xlsx.abstract'

    start_date = fields.Date(string="Start Date", required=True, )
    end_date = fields.Date(string="End Date", required=True, )
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    excel_sheet = fields.Binary()

    def generate_xlsx_report(self, workbook, data, lines):
        lines = self.env['hr.payslip'].browse(data["form"]['hr_payslip_ids'])
        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 12,
            'fg_color': 'white',
        })
        first_header = workbook.add_format({
            'bold': 0,
            'border': 2,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 15,
            'fg_color': '#A3C7F3'
        })
        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 12,
            'valign': 'vcenter',
            'fg_color': '#ededed'
        })

        worksheet = workbook.add_worksheet('hr payslip excel')
        worksheet.right_to_left()
        worksheet.set_column(0, 1, 20)
        worksheet.set_column(2, 3, 40)
        worksheet.set_column(4, 5, 20)
        worksheet.set_paper(9)
        worksheet.set_portrait()

        salary_rule_ids = self.env['hr.salary.rule'].browse(data['form']['hr_salary_rule_ids']) if len(
            data['form']['hr_salary_rule_ids']) > 0 else self.env['hr.salary.rule'].search([], order='sequence asc')
        total_dict = {}
        datas = []
        company_id = self.env['res.company'].browse(data['form']['company_id'])
        buf_image = io.BytesIO(base64.b64decode(company_id.logo))
        worksheet.insert_image(0, 4, 'img.png', {'image_data': buf_image, 'x_scale': 0.15, 'y_scale': 0.15})

        if salary_rule_ids:
            row = 4
            print(str(lines))
            print(str(lines))
            text = 'Salary Report From' + str(lines[0].date_from) + "To" + str(lines[0].date_to)
            worksheet.merge_range('A3:C3', text, table_header_format)
            worksheet.write(2, 0, text, table_header_format)
            col = 0
            for rule in salary_rule_ids:
                worksheet.write(row, col, rule.name, table_header_format)
                total_dict.update({rule.id: 0})
            row += 1
            col = 2
            for slip in lines:
                line = {}
                row += 1
                for slip_line in slip.line_ids:
                    if slip_line.salary_rule_id.id in salary_rule_ids.ids:
                        line['ref'] = slip.number
                        line['code'] = slip.employee_id.pin if slip.employee_id.pin else ""
                        line['slip_name'] = slip.name
                        line['emp_name'] = slip.employee_id.name
                        line['bank_account_id'] = slip.employee_id.bank_account_id.acc_number if slip.employee_id.bank_account_id else ""
                        line['name'] = slip.employee_id.name
                        line['job'] = slip.employee_id.job_title
                        line['start_work'] = slip.employee_id.contract_id.date_start if slip.employee_id.contract_id else ""
                        line['department'] = slip.employee_id.contract_id.department_id.name if slip.employee_id.contract_id else ""
                        if slip_line.amount > 0:
                            line[slip_line.salary_rule_id.id] = slip_line.amount
                            total_dict.update(
                                {slip_line.salary_rule_id.id: total_dict[
                                                                  slip_line.salary_rule_id.id] + slip_line.amount})
                datas.append(line)
            row += 1
            col = 2
            row = 4

            rules_ids = []
            for rl in total_dict:
                if total_dict[rl] > 0:
                    rules_ids.append(rl)
            sal_rule_ids = self.env['hr.salary.rule'].search([('id', 'in', rules_ids)], order='sequence asc')
            col = 0
            worksheet.write(row, col, "#", table_header_format)
            col += 1
            worksheet.write(row, col, "Ref", table_header_format)
            col += 1
            worksheet.write(row, col, "Code", table_header_format)
            col += 1
            worksheet.write(row, col, "Name", table_header_format)
            col += 1
            worksheet.write(row, col, "Job", table_header_format)
            col += 1
            worksheet.write(row, col, "Work Date", table_header_format)
            col += 1
            worksheet.write(row, col, "Department", table_header_format)
            col += 1
            # Header Line
            for sa_line in sal_rule_ids:
                worksheet.write(row, col, sa_line.name, table_header_format)
                col += 1
            # worksheet.write(row, col, "Cash / Bank", table_header_format)
            # col += 1
            # worksheet.write(row, col, "رقم الحساب", table_header_format)
            # col += 1
            row += 1
            ############  Report Lines  ###############
            count = 0
            for line in datas:
                col = 0
                count += 1
                worksheet.write(row, col, count, custom_format)
                col += 1
                worksheet.write(row, col, line['ref'], custom_format)
                col += 1
                worksheet.write(row, col, line['code'], custom_format)
                col += 1
                worksheet.write(row, col, line['name'], custom_format)
                col += 1
                worksheet.write(row, col, line['job'], custom_format)
                col += 1
                worksheet.write(row, col, str(line['start_work']), custom_format)
                col += 1
                worksheet.write(row, col, line['department'], custom_format)
                col += 1
                for sa_line in sal_rule_ids:
                    if sa_line.id in line.keys():
                        worksheet.write(row, col, line[sa_line.id], custom_format)
                    col += 1
                # worksheet.write(row, col, line['bank_account_id'], custom_format)
                # col += 1
                row += 1
            col = 7
            for sa_line in sal_rule_ids:
                for tot in total_dict:
                    if tot == sa_line.id:
                        worksheet.write(row, col, total_dict[tot], table_header_format)
                col += 1
            col += 1
            row += 1

        else:
            raise ValidationError(_('There is no Salary Rules !!'))
