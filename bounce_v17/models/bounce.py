from odoo import fields, models, api


class PayrolStruct(models.Model):
    _inherit = 'hr.payroll.structure'
    is_bounce_deduction = fields.Boolean()


class Bounce(models.Model):
    _name = 'bounce'
    _description = 'Bounce'
    _inherit = ['mail.thread']
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    name = fields.Char('Name')
    date = fields.Date('Date', required=True, default=fields.Date.today())
    type = fields.Selection(string='Calculation base', selection=[
        ('hour', 'Hour'),
        ('day', 'Days'),
        ('fixed', 'Fixed'),
        ('over', 'Over Achievement'),
    ], required=True, )
    value = fields.Float('Value')
    bounce_value = fields.Float('Addition Value', compute="get_bounce_value")
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, )
    # contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id')
    contract_id2 = fields.Many2one('hr.contract', related='employee_id.contract_id')
    type_id = fields.Many2one('bounce.type')
    note = fields.Text(string="Note")
    bounce_id = fields.Many2one('bounce', string="Addition", store=True)
    percentage = fields.Float('Percentage')
    last_value = fields.Float('Last Addition Value', compute="get_last_value")
    # use this field to know it was taken in payslip
    confirmed = fields.Boolean(string='Confirmed', )
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")], string="State", default='draft')
    # company_id = fields.Many2one(comodel_name="res.company", string="", required=False, )

    @api.depends('bounce_id')
    def get_last_value(self):
        for rec in self:
            rec.last_value = 0
            if rec.bounce_id:
                rec.last_value = rec.bounce_id.bounce_value

    @api.onchange('type_id')
    def _onchange_type_id(self):
        self.type = self.type_id.type
        self.value = self.type_id.value

    def confirm(self):
        self.state = 'confirmed'

    def set_draft(self):
        if not self.confirmed:
            self.state = 'draft'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('bounce') or ' '
        return super(Bounce, self).create(values)


    # Continue with your logic

    @api.depends('contract_id2', 'value', 'type', 'bounce_id')
    def get_bounce_value(self):
        for rec in self:
            rec.bounce_value = 0
            if rec.type == 'hour':
                rec.bounce_value = rec.value * rec.contract_id2.hour_value
            elif rec.type == 'day':
                rec.bounce_value = rec.value * rec.contract_id2.day_value
            elif rec.type == 'fixed':
                rec.bounce_value = rec.value
            elif rec.type == 'over':
                if rec.bounce_id:
                    rec.bounce_value = rec.percentage / 100 * rec.bounce_id.bounce_value

    @api.onchange('date', 'percentage')
    def change_date(self):
        for rec in self:
            last_bonuce_id = self.env['bounce'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'confirmed'),
                ('date', '=', self.date),
            ])
            rec.bounce_id = last_bonuce_id.id


class BounceType(models.Model):
    _name = 'bounce.type'

    name = fields.Char('Name', required=True)
    code = fields.Char('code', required=True)
    type = fields.Selection(string='Addition Based On', selection=[
        ('hour', 'Hour'),
        ('day', 'Days'),
        ('fixed', 'Fixed'),
    ], required=True, )
    # ('over', 'Over Achievement'),
    struct_ids = fields.Many2many('hr.payroll.structure', string='Struct')
    value = fields.Float('Value')
    _sql_constraints = [
        ('code_uniq', 'unique (code)', "code already exists !"),
    ]

    @api.model
    def create(self, values):
        res = super(BounceType, self).create(values)
        # struct_id = self.env['hr.payroll.structure'].search([('is_bounce_deduction', '=', True)])
        # struct_ids = res.struct_ids
        # if not struct_id:
        #     struct_id = self.env['hr.payroll.structure'].create({
        #         'name': 'Deduction and Bounce',
        #         'type_id': self.env['hr.payroll.structure.type'].search([], limit=1).id,
        #         'is_bounce_deduction': True,
        #
        #     })
        for struct_id in res.struct_ids:
            self.env['hr.salary.rule'].create({
                'name': res.name,
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'struct_id': struct_id.id,
                'code': res.code,
                'sequence': 50,
                'condition_select': 'none',
                'amount_select': 'code',
                'quantity': 1,
                'amount_python_compute': 'if payslip.bounce_line_ids :   result=sum(payslip.bounce_line_ids.filtered(lambda line:line.bounce_id.type_id.code==\'%s\').mapped("bounce_value"))  '
                                         '\nelse:result=0 ' % res.code,
            })
        return res


class bounce_line(models.Model):
    _name = 'bounce.line'

    hr_payslip_id = fields.Many2one(comodel_name='hr.payslip', string='Payslip', )
    bounce_id = fields.Many2one(comodel_name='bounce', string='Addition', )
    name = fields.Char(string='Type', )
    date = fields.Date(string='Date', )
    notes = fields.Char(string='Notes', )
    bounce_value = fields.Float(string='Value', )


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    bounce_line_ids = fields.One2many(comodel_name='bounce.line', inverse_name='hr_payslip_id', string='Addition Lines')

    # def V(self):
    #     x=sum(self.bounce_line_ids.filtered(lambda line:line.bounce_id.type_id.id==1).mapped('bounce_value'))
    #     print("D::D:d",x)

    @api.onchange('employee_id', 'date_from', 'date_to', 'payslip_run_id')
    def set_bounce_lines(self):
        for rec in self:
            rec.bounce_line_ids = [(5, 0, 0)]
            lines = []
            emp_bonus = self.env['bounce'].search(
                ['&', '&', '&', '&', ('state', '=', 'confirmed'), ('confirmed', '=', False),
                 ('employee_id', '=', rec.employee_id.id), ('date', '>=', rec.date_from), ('date', '<=', rec.date_to)])
            print("11", emp_bonus)
            for bounce_line in emp_bonus:
                print("1")
                lines.append((0, 0,
                              {'bounce_id': bounce_line.id, 'notes': bounce_line.note, 'name': bounce_line.type_id.name,
                               'date': bounce_line.date, 'bounce_value': bounce_line.bounce_value, }))
            rec.bounce_line_ids = lines

    def compute_sheet(self):
        self.set_bounce_lines()
        res = super(hr_payslip, self).compute_sheet()

        return res

    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        for bounce_line in self:
            if bounce_line.bounce_line_ids:
                for bounce in bounce_line.bounce_line_ids:
                    print(bounce.bounce_id.confirmed)
                    bounce.bounce_id.confirmed = True
                    print(bounce.bounce_id.confirmed)
        return res
