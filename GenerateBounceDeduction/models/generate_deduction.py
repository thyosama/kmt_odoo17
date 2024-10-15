from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class BounceInhrt(models.Model):
    _inherit = 'deduction'
    
    generate_deduction_id = fields.Many2one('generate.deduction')


class generatededuction(models.Model):
    _name = 'generate.deduction'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    date = fields.Date('From Date', required=True, default=fields.Date.today())
    type = fields.Selection(string='deduction Based On',
                            selection=[('hour', 'Hour'),
                                       ('day', 'Days'),
                                       ('fixed', 'Fixed'), ], required=True, )
    value = fields.Float('Value')
    deduction_value = fields.Float('deduction Value', compute="get_deduction_value")
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, )
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id')
    type_id = fields.Many2one('deduction.type')
    note = fields.Text(string="Note")
    # use this field to know it was taken in payslip
    confirmed = fields.Boolean(string='Confirmed', )
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")], string="State", default='draft')
    no_month = fields.Integer('No.Months')
    deduction_ids = fields.One2many(comodel_name='deduction', inverse_name='generate_deduction_id')
    deduction_count = fields.Integer(compute="get_deduction_count")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    position_id = fields.Many2one('hr.job', related='employee_id.job_id')
    emp_badge = fields.Char(related='employee_id.barcode')


    @api.depends('deduction_ids')
    def get_deduction_count(self):
        for rec in self:
            rec.deduction_count = len(rec.deduction_ids.ids)

    @api.onchange('type_id')
    def _onchange_type_id(self):
        self.type = self.type_id.type
        self.value = self.type_id.value

    def set_draft(self):
        if not self.confirmed:
            self.state = 'draft'

    def confirm(self):
        for i in range(0, self.no_month):
            deduction_info = {
                'generate_deduction_id': self.id,
                'employee_id': self.employee_id.id,
                'contract_id': self.contract_id.id,
                'type_id': self.type_id.id,
                'type': self.type,
                'value': self.value,
                'deduction_value': self.deduction_value,
                'date': self.date + relativedelta(months=i)
            }
            self.env['deduction'].create(deduction_info)
        self.state = 'confirmed'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('deduction1') or ' '
        return super(generatededuction, self).create(values)

    @api.depends('contract_id', 'value', 'type')
    def get_deduction_value(self):
        for rec in self:
            rec.deduction_value = 0
            if rec.type == 'hour':
                rec.deduction_value = rec.value * rec.contract_id.hour_value
            elif rec.type == 'day':
                rec.deduction_value = rec.value * rec.contract_id.day_value
            elif rec.type == 'fixed':
                rec.deduction_value = rec.value

    def action_open_deductions(self):
        self.ensure_one()
        action = self.env.ref("deduction_v17.deduction_action").read()[0]
        action["domain"] = [("id", "in", self.deduction_ids.ids)]
        return action
