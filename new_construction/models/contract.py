from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class contract(models.Model):
    _name = 'construction.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name = fields.Char("Name", compute='_get_name')
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type", default='owner')
    project_id = fields.Many2one("project.project", string="Project")
    partner_id_2 = fields.Many2one("res.partner", string="Customer", store=True, index=True)
    date = fields.Date("Date", default=datetime.today())
    recieve_date = fields.Date("Receive Date")
    contract_id = fields.Many2one("construction.contract.user", string="Contract", domain="[('type','=',type)]")
    account_id = fields.Many2one(related="contract_id.account_id", string="Partner Account", store=True, index=True)

    down_payment_prectenge = fields.Float("Down Payment %")
    down_payment_value = fields.Float("Down Payment Value", compute="calculate_down_payment",
                                      store=True, index=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    revenue_account_id = fields.Many2one(related='contract_id.counterpart_account_id', store=True, index=True,
                                         string="Revenue Account")
    lines_id = fields.One2many("construction.contract.line", "contract_id", readonly=False)
    sub_lines_id = fields.One2many("construction.contract.line", "sup_contract_id")

    total_value = fields.Float(compute='_get_total_value', string="Contract Value")
    deduction_ids = fields.One2many("contract.deduction.allowance.lines", "contract_id",
                                    string="Deductions", domain=[('type', '=', 'deduction')])
    allowance_ids = fields.One2many("contract.deduction.allowance.lines", "contract_id",
                                    string="Allowance", domain=[('type', '=', 'addition')])

    sub_contactor = fields.Many2one("res.partner", string="sub contractor Name")
    date = fields.Date("Date", default=datetime.today())
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string="State", default='draft')
    referance = fields.Char()

    is_sub_contract = fields.Boolean()
    partial_contract = fields.Many2one('construction.contract')
    stage_ids = fields.One2many(
        comodel_name='contract.stage.line',
        inverse_name='contract_id',
        string='stages',
        required=False)



    count_sub = fields.Integer(compute='get_count_sub')
    count_eng = fields.Integer(compute='get_count_sub')

    @api.onchange("project_id")
    def _onchnage_project_id(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id_2 = self.project_id.partner_id.id

    @api.depends('project_id')
    def get_count_sub(self):
        for rec in self:
            rec.count_sub = rec.count_eng = 0
            sub_ids = self.env['construction.contract'].search([('partial_contract', '=', self.id)])
            con_ids = self.env['construction.engineer'].search([('contract_id', '=', self.id)])
            if sub_ids:
                rec.count_sub = len(sub_ids)
            if con_ids:
                rec.count_eng = len(con_ids)

    @api.constrains('stage_ids')
    def check_stage_ids(self):
        total_prec = 0
        for rec in self.stage_ids:
            total_prec += rec.prec
        if self.stage_ids and (total_prec < 100 or total_prec > 100):
            raise ValidationError("Please prec must be equal 100")

    def view_partial_contract(self):
        view = self.env.ref('new_construction.view_contract_tree_sub_contract')
        if self.type == 'supconstractor':
            view_form = self.env.ref('new_construction.view_contract_form_sub')
        else:
            view_form = self.env.ref('new_construction.view_contract_form_sub_contract_view')

        return {
            'name': ('Sub Contract'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            'res_model': 'construction.contract',
            'domain': [('partial_contract', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_partial_contract': self.id},
            'target': 'current'
        }

    def view_engineer_tem(self):
        return {
            'name': ('Template'),
            'view_mode': 'tree,form',
            'res_model': 'construction.engineer',
            'domain': [('contract_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def create_partial_contract(self):
        if self.type == 'supconstractor':
            view = self.env.ref('new_construction.view_contract_form_sub')
        else:
            view = self.env.ref('new_construction.view_contract_form')

        return {
            'name': ('SUB Contract'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'construction.contract',
            'type': 'ir.actions.act_window',

            'target': 'new',
            'context': {
                'default_project_id': self.project_id.id,
                'default_partner_id_2': self.partner_id_2.id,
                'default_contract_id': self.contract_id.id,
                'default_account_id': self.account_id.id,
                'default_revenue_account_id': self.revenue_account_id.id,
                'default_partial_contract': self.id,
                'default_is_sub_contract': True
            }
        }

    @api.depends('create_date')
    def _get_name(self):

        for rec in self:
            if rec.type == 'owner':
                rec.name = 'Owner Contract  /' + str(rec.project_id.name) + " /" + str(rec.id).zfill(4)
            elif rec.type == 'supconstractor':
                rec.name = str(rec.project_id.name) + "/" + rec.sub_contactor.name + " /" + str(rec.id).zfill(4)

    @api.depends('lines_id')
    def _get_total_value(self):
        for rec in self:
            rec.total_value = 0
            for record in rec.lines_id:
                rec.total_value += record.total_value
            # if rec.type == 'owner':
            #     for record in rec.lines_id:
            #         rec.total_value += record.total_value
            # elif rec.type == 'supconstractor':
            #     for record in rec.sub_lines_id:
            #         rec.total_value += record.total_value

    @api.depends('down_payment_prectenge', 'total_value')
    def calculate_down_payment(self):
        for rec in self:
            rec.down_payment_value = (rec.down_payment_prectenge / 100) * rec.total_value

    def action_confirm(self):
        self.state = 'confirm'

    def create_engineer_template(self):

        tem_id = self.env['construction.engineer'].create({
            'contract_id': self.id,
            'project_id': self.project_id.id,
        })
        # for rec in self.stage_ids:
        #     self.create_engineer_tem(self.project_id, rec.stage_id, tem_id, rec.prec)
        # for rec in self.lines_id:
        #     if rec.stage_line_ids:
        #
        #         for st in rec.stage_line_ids:
        #
        #             main_stage_id = self.env['contract.stage.line'].search(
        #                 [('contract_id', '=', rec.contract_id.id), ('stage_id', '=', st.id)])
        #             other_prec = 0
        #             if main_stage_id:
        #                 other_prec = main_stage_id.prec
        #
        #             m_qty = self.get_remind_qty(rec.id)
        #             if m_qty == 0:
        #                 m_qty = rec.qty
        #             self.env['construction.engineer.lines'].create({
        #                 'parent_id': tem_id.id,
        #                 # 'tender_id': rec.tender_id if rec.tender_id else '',
        #                 'stage_id': st.stage_id.id,
        #                 'remind_qty': abs(m_qty - ((rec.qty * other_prec) / 100)),
        #                 'qty': (rec.qty * st.prec) / 100,
        #                 'tender_qty': rec.qty,
        #                 'contract_line_id': rec.id,
        #                 'item': rec.item.id,
        #                 'uom_id': rec.uom_id.id,
        #                 'other_prec':  st.prec,
        #                 'related_job': rec.related_job.id if rec.related_job else '',
        #                 'name': rec.name
        #
        #             })
        # sub_contract_ids = self.env['construction.contract'].search([('partial_contract', '=', self.id)])
        # for rec in sub_contract_ids.lines_id:
        #     if rec.stage_line_ids:
        #         for st in rec.stage_line_ids:
        #
        #             main_stage_id = self.env['contract.stage.line'].search(
        #                 [('contract_id', '=', rec.contract_id.id), ('stage_id', '=', st.id)])
        #             other_prec = 0
        #             if main_stage_id:
        #                 other_prec = main_stage_id.prec
        #
        #             m_qty = self.get_remind_qty(rec.id)
        #             if m_qty == 0:
        #                 m_qty = rec.qty
        #             self.env['construction.engineer.lines'].create({
        #                 'parent_id': tem_id.id,
        #                 'tender_id': rec.tender_id if rec.tender_id else '',
        #                 'stage_id': st.stage_id.id,
        #                 'remind_qty': abs(m_qty - ((rec.qty * other_prec) / 100)),
        #                 'qty': (rec.qty * st.prec) / 100,
        #                 'tender_qty': rec.qty,
        #                 'contract_line_id': rec.id,
        #                 'item': rec.item.id,
        #                 'uom_id': rec.uom_id.id,
        #                 'other_prec':  st.prec,
        #                 'related_job': rec.related_job.id if rec.related_job else '',
        #                 'name': rec.name
        #
        #             })

    def create_engineer_tem(self, project_id, stage, tem_id, prec):

        sub_contract_ids = self.env['construction.contract'].search([('partial_contract', '=', self.id)])
        for rec in self.lines_id:
            if rec.display_type == False and not rec.stage_line_ids:

                m_qty = self.get_remind_qty(rec.id)
                if m_qty == 0:
                    m_qty = rec.qty
                self.env['construction.engineer.lines'].create({
                    'parent_id': tem_id.id,
                    # 'tender_id': rec.tender_id if rec.tender_id else '',
                    'stage_id': stage.id,
                    'remind_qty': abs(m_qty - ((rec.qty * prec) / 100)),
                    'qty': (rec.qty * prec) / 100,
                    'tender_qty': rec.qty,
                    'contract_line_id': rec.id,
                    'item': rec.item.id,
                    'other_prec': prec,
                    'uom_id': rec.uom_id.id,
                    'related_job': rec.related_job.id if rec.related_job else '',
                    'name':rec.name

                })



            elif rec.display_type and not rec.stage_line_ids:
                print("====================================================================", rec.name)
                self.env['construction.engineer.lines'].create({
                    'parent_id': tem_id.id,
                    'display_type': rec.display_type,
                    'name': rec.name,
                    'contract_line_id': rec.id

                })
        if sub_contract_ids:
            for rec in sub_contract_ids.lines_id:
                if rec.display_type == False:
                    if not rec.stage_line_ids:
                        m_qty = self.get_remind_qty(rec.id)
                        if m_qty == 0:
                            m_qty = rec.qty
                        self.env['construction.engineer.lines'].create({
                            'parent_id': tem_id.id,
                            'tender_id': rec.tender_id if rec.tender_id else '',
                            'stage_id': stage.id,
                            'remind_qty': abs(m_qty - ((rec.qty * prec) / 100)),
                            'qty': (rec.qty * prec) / 100,
                            'tender_qty': rec.qty,
                            'contract_line_id': rec.id,
                            'item': rec.item.id, 'other_prec': prec,
                            'uom_id': rec.uom_id.id,
                            'related_job': rec.related_job.id if rec.related_job else '',
                            'name': rec.name

                        })

                elif rec.display_type and not rec.stage_line_ids:
                    self.env['construction.engineer.lines'].create({
                        'parent_id': tem_id.id,
                        'display_type': rec.display_type,
                        'name': rec.name,

                    })

    def get_remind_qty(self, tender):
        lines = self.env['construction.engineer.lines'].search(
            [('contract_line_id', '=', tender), ('parent_id.state', '!=', 'cancel')])

        qty = sum(lines.mapped('qty'))
        return qty


class ContractLine(models.Model):
    _name = 'construction.contract.line'
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    code = fields.Char("Code")
    contract_id = fields.Many2one("construction.contract")
    sup_contract_id = fields.Many2one("construction.contract")
    item = fields.Many2one('product.item', string='Item')
    name = fields.Text("Description")
    sequence = fields.Integer(string='Sequence', default=10)
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    qty = fields.Float("Quantity")
    notes = fields.Char("Notes")
    price_unit = fields.Float("Price Unit ", )
    discount = fields.Float("Discount % ", )
    total_value = fields.Float("Total value ", compute='_get_total_value', store=True, index=True)
    sub_contarctor_item = fields.Many2one('construction.subconstractor', string="SubConstractor")
    tender_id = fields.Char(string="Tender ID")

    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type", default='owner')

    is_sub_contract = fields.Boolean(related='contract_id.is_sub_contract')
    related_job = fields.Many2one(related='item.related_job')
    state = fields.Selection(related="contract_id.state")
    # stages_id = fields.Many2many(
    #     comodel_name='contract.stage',
    #     string='Stages')

    stage_line_ids = fields.One2many("contract.line.stage.line", "contract_line_id")

    @api.constrains('stage_line_ids')
    def constain_stage_ids(self):
        perc = 0
        for record in self:
            perc = 0
            for rec in record.stage_line_ids:
                perc += rec.prec
            print(">")
            if perc != 100:
                raise ValidationError("Percentage must be equal 100")

    def add_stage_line_ids(self):
        view_id = self.env.ref('new_construction.contract_line_stage_view_form')
        return {
            'name': ('Stages'),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id.id,
            'res_model': 'construction.contract.line',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            # 'context': {'default_contract_line_id': self.id},
            'target': 'new'
        }

    def view_stage_line_ids(self):
        view_tree = self.env.ref('new_construction.view_contract_form_sub')

        view_form = self.env.ref('new_construction.contract_line_stage_view_form')
        view_id = self.env.ref('new_construction.contract_line_stage_view_form')

        return {
            'name': ('Stages'),
            'view_mode': 'form',
            # 'views': [(view_tree.id, 'tree'), (view_form.id, 'form')],
            'view_id': view_id.id,
            'res_model': 'construction.contract.line',
            'type': 'ir.actions.act_window',
            # 'context': {'default_contract_line_id': self.id},
            # 'domain': [('contract_line_id', '=', self.id)],
            'res_id':self.id,
            'target': 'new'
        }

    # @api.onchange('contract_id.stage_ids', 'stages_id')
    # def get_states_line(self):
    #     if self._origin.contract_id:
    #         ids = []
    #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
    #         for rec in self.contract_id.stage_ids:
    #             ids.append(rec.id)
    #         domain = {'stages_id': [('id', 'in', ids)]}
    #         return {'domain': domain}

    _sql_constraints = [
        ('code_uniq_contract', 'UNIQUE (code,contract_id)', 'You can not have  the same code !')
    ]

    @api.depends("price_unit", "qty", "discount")
    def _get_total_value(self):
        for rec in self:
            value = rec.price_unit * rec.qty
            rec.total_value = (value) - (value * (rec.discount / 100))

    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('sub_contarctor_item', 'code')
    def _onchange_tender_id(self):

        # if  self.sub_contarctor_item:

        sub_contractors = []
        job_cost_id = self.env['construction.job.cost'].search([
            ('project_id', '=', self.contract_id.project_id.id),
            ('code', '=', self.code),
        ])

        for job_cost in job_cost_id:
            # print(job_cost, "Line", job_cost.subconstractor_ids)
            for line in job_cost.subconstractor_ids:
                sub_contractors.append(line.id)
        job_id = self.env['construction.job.cost'].search([('code', '=', self.code)], limit=1)
        if job_id and self.sub_contarctor_item:
            sub_con = self.env['construction.subconstractor'].search(
                [('job_id', '=', job_id.id), ('id', '=', self.sub_contarctor_item.id)], limit=1)
            self.price_unit = sub_con.cost_unit
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>0",job_cost_id,sub_contractors)

        return {'domain': {'sub_contarctor_item': [('id', 'in', sub_contractors)]}}

