from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class BounceInhrt(models.Model):
    _inherit = 'bounce'
    
    generate_bounce_id = fields.Many2one('generate.bounce')


class GenerateBounce(models.Model):
    _name = 'generate.bounce'
    _description = 'Generate Bounce'
    _inherit = ['mail.thread']
    
    name = fields.Char('Name')
    date = fields.Date('From Date', required=True, default=fields.Date.today())
    type = fields.Selection(string='Addition Based On',
                            selection=[('hour', 'Hour'),
                                       ('day', 'Days'),
                                       ('fixed', 'Fixed'), ], required=True, )
    value = fields.Float('Value')
    bounce_value = fields.Float('Addition Value', compute="get_bounce_value")
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, )
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id')
    type_id = fields.Many2one('bounce.type')
    note = fields.Text(string="Note")
    # use this field to know it was taken in payslip
    confirmed = fields.Boolean(string='Confirmed', )
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")], string="State", default='draft')
    no_month = fields.Integer('No.Months')
    bounce_ids = fields.One2many(comodel_name='bounce', inverse_name='generate_bounce_id')
    bounce_count = fields.Integer(compute="get_bounce_count")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    position_id = fields.Many2one('hr.job', related='employee_id.job_id')
    emp_badge = fields.Char(related='employee_id.barcode')

    @api.depends('bounce_ids')
    def get_bounce_count(self):
        for rec in self:
            rec.bounce_count = len(rec.bounce_ids.ids)

    @api.onchange('type_id')
    def _onchange_type_id(self):
        self.type = self.type_id.type
        self.value = self.type_id.value

    def confirm(self):
        for i in range(0, self.no_month):
            bounce_info = {
                'generate_bounce_id': self.id,
                'employee_id': self.employee_id.id,
                'contract_id': self.contract_id.id,
                'type_id': self.type_id.id,
                'type': self.type,
                'value': self.value,
                'bounce_value': self.bounce_value,
                'date': self.date + relativedelta(months=i)
            }
            self.env['bounce'].create(bounce_info)
        self.state = 'confirmed'

    def set_draft(self):
        if not self.confirmed:
            self.state = 'draft'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('bounce1') or ' '
        return super(GenerateBounce, self).create(values)

    @api.depends('contract_id', 'value', 'type')
    def get_bounce_value(self):
        for rec in self:
            rec.bounce_value = 0
            if rec.type == 'hour':
                rec.bounce_value = rec.value * rec.contract_id.hour_value
            elif rec.type == 'day':
                rec.bounce_value = rec.value * rec.contract_id.day_value
            elif rec.type == 'fixed':
                rec.bounce_value = rec.value

    def action_open_bounces(self):
        self.ensure_one()
        action = self.env.ref("bounce_v17.bounce_action").read()[0]
        action["domain"] = [("id", "in", self.bounce_ids.ids)]
        return action
