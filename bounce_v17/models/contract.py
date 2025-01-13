from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    hour_value = fields.Float(string='Hour Value', )
    worked_dys = fields.Float(string='hours Per Day', )
    day_value = fields.Float(string='Day Value', compute="get_day_value")

    x_variable_salary = fields.Monetary(string="Variable Salary", required=False, )

    @api.depends('hour_value', 'worked_dys')
    def get_day_value(self):
        for rec in self:
            print(rec.hour_value, "           ", rec.worked_dys)
            rec.day_value = rec.hour_value * rec.worked_dys



