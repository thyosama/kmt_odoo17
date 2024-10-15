from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    all_emp_count = fields.Integer(compute="compute_all_emp", string="All Employee")
    disability_emp_count = fields.Integer(compute="compute_all_emp", string="Disability Employee")
    disability_percentage = fields.Float(compute="compute_all_emp", string="Percentage")

    @api.depends('name')
    def compute_all_emp(self):
       for rec in self:
           emp_ids = self.env['hr.employee'].search([])
           rec.all_emp_count = len(emp_ids.ids)-1 if len(emp_ids.ids)>0 else 0
           dis_emp_ids = self.env['hr.employee'].search([('disability', '=', True)])
           rec.disability_emp_count = len(dis_emp_ids.ids)
           if len(dis_emp_ids.ids) > 0 and  len(emp_ids.ids)>0:
               rec.disability_percentage = len(dis_emp_ids.ids) / (len(emp_ids.ids)-1) * 100
           else:
               rec.disability_percentage = 0
