from odoo import fields, models, api


class PayrolStruct(models.Model):
    _inherit = 'hr.payroll.structure'
    is_bounce_deduction = fields.Boolean()


class deduction(models.Model):
    _name = 'deduction'
    _description = 'Deduction'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    date = fields.Date('Date', required=True, default=fields.Date.today())
    type = fields.Selection(string='Calculation Base',
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

    @api.onchange('type_id')
    def _onchange_type_id(self):
        self.type = self.type_id.type
        self.value = self.type_id.value

    def set_draft(self):
        if not self.confirmed:
            self.state = 'draft'

    def confirm(self):
        self.state = 'confirmed'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('deduction') or ' '
        return super(deduction, self).create(values)

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


class deductionType(models.Model):
    _name = 'deduction.type'

    name = fields.Char('Name', required=True)
    code = fields.Char('code', required=True)
    type = fields.Selection(string='Deduction Based On', selection=[
        ('hour', 'Hour'),
        ('day', 'Days'),
        ('fixed', 'Fixed'),
    ], required=True, )
    #   ('over', 'Over Achievement'),
    value = fields.Float('Value')
    struct_ids = fields.Many2many('hr.payroll.structure', string='Struct')
    _sql_constraints = [
        ('code_uniq', 'unique (code)', "code already exists !"),
    ]

    @api.model
    def create(self, values):
        res = super(deductionType, self).create(values)
        struct_id = self.env['hr.payroll.structure'].search([('is_bounce_deduction', '=', True)])
        if not struct_id:
            struct_id = self.env['hr.payroll.structure'].create({
                'name': 'Deduction and Bounce',
                'type_id': self.env['hr.payroll.structure.type'].search([], limit=1).id,
                'is_bounce_deduction': True,

            })
        self.env['hr.salary.rule'].create({
            'name': res.name,
            'category_id': self.env.ref('hr_payroll.DED').id,
            'code': res.code,
            'struct_id': struct_id.id,
            'sequence': 50,
            'condition_select': 'none',
            'amount_select': 'code',
            'quantity': 1,
            'amount_python_compute': 'if payslip.deduction_line_ids :  result=-sum(payslip.deduction_line_ids.filtered(lambda line:line.deduction_id.type_id.code==\'%s\').mapped("deduction_value"))'
                                     '\nelse:result=0 ' % res.code,

        })
        return res


class deduction_line(models.Model):
    _name = 'deduction.line'

    hr_payslip_id = fields.Many2one(comodel_name='hr.payslip', string='Payslip', )
    deduction_id = fields.Many2one(comodel_name='deduction', string='deduction', )
    name = fields.Char(string='Type', )
    date = fields.Date(string='Date', )
    notes = fields.Char(string='Notes', )
    deduction_value = fields.Float(string='Value', )


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    deduction_line_ids = fields.One2many(comodel_name='deduction.line', inverse_name='hr_payslip_id',
                                         string='Bounes Lines')

    def return_deduction_len(self):

        return int(len(self.deduction_line_ids.ids))

    # def V(self):
    #     x=sum(self.deduction_line_ids.filtered(lambda line:line.deduction_id.type_id.id==1).mapped('deduction_value'))
    #     print("D::D:d",x)

    @api.onchange('employee_id', 'date_from', 'date_to', 'payslip_run_id')
    def set_deduction_lines(self):
        for rec in self:
            rec.deduction_line_ids = [(5, 0, 0)]
            lines = []
            emp_bonus = self.env['deduction'].search([
                '&', '&', '&', '&', ('state', '=', 'confirmed'),
                ('confirmed', '=', False),
                ('employee_id', '=', rec.employee_id.id),
                ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to)
            ])
            print("11", emp_bonus)
            for deduction_line in emp_bonus:
                print("1")
                lines.append((0, 0, {'deduction_id': deduction_line.id, 'notes': deduction_line.note,
                                     'name': deduction_line.type_id.name, 'date': deduction_line.date,
                                     'deduction_value': deduction_line.deduction_value, }))
            rec.deduction_line_ids = lines

    def compute_sheet(self):
        self.set_deduction_lines()
        res = super(hr_payslip, self).compute_sheet()

        return res

    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        for deduction_line in self:
            if deduction_line.deduction_line_ids:
                for deduction in deduction_line.deduction_line_ids:
                    print(deduction.deduction_id.confirmed)
                    deduction.deduction_id.confirmed = True
                    print(deduction.deduction_id.confirmed)
        return res
