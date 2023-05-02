from odoo.exceptions import ValidationError

from odoo import models, fields, api
from datetime import datetime


class Tender(models.Model):
    _name = "construction.job.cost"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name = fields.Char(compute='get_name')
    project_id = fields.Many2one("project.project", string="Project")
    code = fields.Char("Code")
    # type = fields.Selection([('main','Main'),('transcation','Transcation')],string ='Type',default='main')
    item = fields.Many2one('product.item', string='Item')
    parent_item = fields.Many2one('product.item', string='Parent Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    qty = fields.Float("Quantity")
    status = fields.Selection([('main', 'Main'), ('renew', 'Renewal')], string="Status", default='main')
    notes = fields.Char("Notes")
    tender_id = fields.Many2one("construction.tender")
    date = fields.Date("Date", default=datetime.today())
    start_date = fields.Date("Start Date", default=datetime.today())
    end_date = fields.Date("End Date")
    dif = fields.Char("Differance Date", compute='_get_dif')
    partner_id = fields.Many2one("res.partner", "Customer")

    material_ids = fields.One2many('construction.material', "job_id")
    total_material = fields.Float(compute='_compute_total_material', string="Material", store=True, index=True)
    labour_ids = fields.One2many('construction.labour', "job_id")
    total_labour = fields.Float(compute='_compute_total_labour', string="Labours", store=True, index=True)
    expense_ids = fields.One2many('construction.expense', "job_id")
    total_expense = fields.Float(compute='_compute_total_expense', string="Expenses", store=True, index=True)
    subconstractor_ids = fields.One2many('construction.subconstractor', "job_id")
    total_subconstractor = fields.Float(compute='_compute_total_subconstractor', string="SubContractor", store=True,
                                        index=True)
    equipment_ids = fields.One2many('construction.equipment', "job_id")
    total_equipment = fields.Float(compute='_compute_total_equipment', string="Equipment", store=True, index=True)
    total_value_all = fields.Float(compute='_compute_all_values', string="Total", store=True, index=True)
    is_template = fields.Boolean(default=False)
    job_template = fields.Many2one('construction.job.cost', string="Break Down Template",
                                   domain="[('is_template','=',True)]")

    state = fields.Selection([('draft', 'draft'), ('confirm', 'Confirm'), ('approve', 'Approve'),
                              ('quotation', 'Financial Offer')], string="State", default="draft")
    sales_price_update = fields.Float("Sales Price")
    name2 = fields.Char("Name")
    total_material_with_qty = fields.Float(string='Material', compute="compute_total_with_qty", store=True, index=True)
    total_labour_with_qty = fields.Float(string='Labour', compute="compute_total_with_qty", store=True, index=True)
    total_expenses_with_qty = fields.Float(string='Expense', compute="compute_total_with_qty", store=True, index=True)
    total_subcontractor_with_qty = fields.Float(string='Subcontractor', compute="compute_total_with_qty", store=True,
                                                index=True)
    total_equipment_with_qty = fields.Float(string='Equipment', compute="compute_total_with_qty", store=True,
                                            index=True)
    total_value_all_with_qty = fields.Float(string='Total', compute="compute_total_with_qty", store=True, index=True)
    active = fields.Boolean(default=True)
    related_job = fields.Many2one("tender.related.job")
    currancy_id = fields.Many2one("res.currency")
    version = fields.Char()
    version_num = fields.Integer()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    techical_type = fields.Boolean()

    unit_type = fields.Selection([('unit', 'Unit'), ('total', 'Total')], default='unit')

    unit_type = fields.Selection([('unit','Unit'),('total','Total')],default='unit')
    show_taxes = fields.Boolean(compute='_compute_show_taxes', readonly=False)
    show_cost_per_unit = fields.Boolean(compute='_compute_show_cost_per_unit', readonly=False)

    @api.model
    def _get_default_company(self):
        return self.env["res.company"].browse(self.env.company.id)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=_get_default_company)

    @api.depends('company_id.show_taxes')
    def _compute_show_taxes(self):
        for rec in self:
            rec.show_taxes = rec.company_id.show_taxes
    @api.depends('company_id.show_cost_per_unit')
    def _compute_show_cost_per_unit(self):
            for rec in self:
                rec.show_cost_per_unit = rec.company_id.show_cost_per_unit


    @api.depends('material_ids', 'equipment_ids', 'labour_ids', 'expense_ids', 'subconstractor_ids', 'equipment_ids',
                 'qty')
    def compute_total_with_qty(self):
        for record in self:
            record.total_material_with_qty = sum(line.cost_subtotal for line in record.material_ids) * record.qty
            record.total_labour_with_qty = sum(line.cost_subtotal for line in record.labour_ids) * record.qty
            record.total_expenses_with_qty = sum(line.cost_subtotal for line in record.expense_ids) * record.qty
            record.total_subcontractor_with_qty = sum(
                line.cost_subtotal for line in record.subconstractor_ids) * record.qty
            record.total_equipment_with_qty = sum(line.cost_subtotal for line in record.equipment_ids) * record.qty
            record.total_value_all_with_qty = record.total_material_with_qty + record.total_labour_with_qty + record.total_expenses_with_qty + record.total_subcontractor_with_qty + record.total_equipment_with_qty
            # for line in record.material_ids:
            #     material += line.cost_subtotal
            # for line in record.labour_ids:
            #     labour += line.cost_subtotal
            # for line in record.expense_ids:
            #     expenses += line.cost_subtotal
            # for line in record.subconstractor_ids:
            #     subcontractor += line.cost_subtotal
            # for line in record.equipment_ids:
            #     equipment += line.cost_subtotal
            #

    @api.depends('code', 'project_id', 'name2')
    def get_name(self):
        for rec in self:
            name = ''
            if rec.project_id:
                name += rec.project_id.name + "/"
            if rec.description:
                name += rec.description + "/"
            if rec.code:
                name += rec.code
            if rec.name2:
                name = rec.name2
            rec.name = name

    def action_confirm(self):
        check = False
        if len(self.material_ids) > 0:
            check = True
        if len(self.expense_ids) > 0:
            check = True
        if len(self.equipment_ids) > 0:
            check = True
        if len(self.subconstractor_ids) > 0:
            check = True
        if len(self.labour_ids) > 0:
            check = True
        if check == False:
            raise ValidationError("Please add at least one line")

        self.state = 'confirm'

    def action_approve(self):
        self.state = 'approve'
        self.tender_id.state = 'job_estimate'
        if self.techical_type == False:
            self.tender_id.price_unit = self.total_value_all
        # self.tender_id.total_value = self.total_value_all_with_qty

    def action_quotation(self):
        self.state = 'quotation'
        # self.project_id.create_quotation()

    @api.onchange('job_template')
    def _get_job_template(self):
        values = []
        for rec in self.job_template:
            if rec.material_ids:
                for mat in rec.material_ids:
                    values.append((0, 0, {
                        'product_id': mat.product_id.id,
                        'description': mat.description,
                        'uom_id': mat.uom_id.id, 'qty': mat.qty,
                        'waste': mat.waste, 'cost_unit': mat.cost_unit

                    }))

                self.material_ids = values
            if rec.labour_ids:
                values = []

                for lab in rec.labour_ids:
                    values.append((0, 0, {
                        'product_id': lab.product_id.id,
                        'description': lab.description,
                        'uom_id': lab.uom_id.id, 'planned_qty': lab.planned_qty,
                        'cost_unit': lab.cost_unit

                    }))
                self.labour_ids = values

            if rec.expense_ids:
                values = []

                for exp in rec.expense_ids:
                    values.append((0, 0, {
                        'product_id': exp.product_id.id,
                        'description': exp.description,
                        'uom_id': exp.uom_id.id, 'planned_qty': exp.planned_qty,
                        'cost_unit': exp.cost_unit

                    }))
                self.expense_ids = values
            if rec.subconstractor_ids:
                values = []
                for sub in rec.subconstractor_ids:
                    values.append((0, 0, {
                        'product_id': sub.product_id.id,
                        'description': sub.description,
                        'uom_id': sub.uom_id.id, 'planned_qty': sub.planned_qty,
                        'cost_unit': sub.cost_unit

                    }))
                self.subconstractor_ids = values
            if rec.equipment_ids:
                values = []
                for equip in rec.equipment_ids:
                    values.append((0, 0, {
                        'product_id': sub.product_id.id,
                        'description': sub.description,
                        'uom_id': sub.uom_id.id, 'planned_qty': sub.planned_qty,
                        'cost_unit': sub.cost_unit

                    }))
                self.equipment_ids = values

    @api.onchange("end_date")
    def _onchange_check_end_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End Date Must be greater than Start Date")

    @api.constrains("end_date")
    def _check_end_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End Date Must be greater than Start Date")

    @api.depends('start_date', 'end_date')
    def _get_dif(self):
        self.dif = ''
        for rec in self:
            dif = ''
            if rec.start_date and rec.end_date:
                self.dif = rec.end_date - rec.start_date

    @api.depends("material_ids", 'total_material', 'total_labour', 'total_expense', 'total_subconstractor',
                 'total_equipment')
    def _compute_all_values(self):
        for rec in self:
            self.total_value_all = \
                rec.total_material + rec.total_labour + rec.total_expense + rec.total_subconstractor + rec.total_equipment

    @api.depends('equipment_ids')
    def _compute_total_equipment(self):
        self.total_equipment = 0
        for record in self:
            for rec in record.equipment_ids:
                record.total_equipment += rec.cost_subtotal

    @api.depends('subconstractor_ids')
    def _compute_total_subconstractor(self):
        self.total_subconstractor = 0
        for record in self:
            for rec in record.subconstractor_ids:
                record.total_subconstractor += rec.cost_subtotal

    @api.depends('expense_ids')
    def _compute_total_expense(self):
        self.total_expense = 0
        for record in self:
            for rec in record.expense_ids:
                record.total_expense += rec.cost_subtotal

    @api.depends('labour_ids')
    def _compute_total_labour(self):
        self.total_labour = 0
        for record in self:
            for rec in record.labour_ids:
                record.total_labour += rec.cost_subtotal

    @api.depends('material_ids', 'material_ids.currancy_id', 'material_ids.ratio')
    def _compute_total_material(self):
        self.total_material = 0
        for record in self:
            for rec in record.material_ids:
                record.total_material += rec.cost_subtotal

    def update_sales_price(self):

        view_form = self.env.ref('construction.view_job_cost_fromm_update')

        return {
            'name': ('Update'),
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(view_form.id, 'form')],
            'res_model': 'construction.job.cost',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def update_price(self):
        self.indirect_amount = 0
        self.indirect_percentage = 0
        self.profit_type = 'amount'

        self.profit_amount = self.sales_price_update - self.total_value_all
        # self.gross_profit = self.sales_price_update-self.total_value_all
        self.sales_price = self.sales_price_update

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("You Can delete only draft Job")
        res = super(Tender, self).unlink()

        return res

    @api.onchange("qty")
    def _onchange_total_qty_line(self):
        for rec in self.material_ids:
            if self.unit_type == 'total':

                if rec.total_qty_line > 0 and self.qty > 0:
                    rec.qty = rec.total_qty_line / self.qty


class Material(models.Model):
    _name = "construction.material"
    product_id = fields.Many2one("product.product", string="Product", required=True \
                                 , domain=[('material', '=', True)])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity", required=True)
    waste = fields.Float("Waste %")
    planned_qty = fields.Float("Planned Qty", default=1, compute='_get_planned_cost')
    cost_unit = fields.Float(string="Cost/unit", required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total', string='price Cost sub total')
    cost_subtotal_before_discount = fields.Float(compute='_compute_sub_total', string='price Cost subtotal %')
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    item = fields.Many2one(related='job_id.item', string='Item')
    total_value = fields.Float(compute='_compute_total_value', string='Total Value')
    active = fields.Boolean(default=True)
    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())
    ratio = fields.Float(default=1, string="Rate")
    tax_ids = fields.Many2many(comodel_name='account.tax',string='taxes')
    cost_per_unit = fields.Float(compute='_compute_cost_per_unit')
    waste_cost = fields.Float(compute='_compute_cost_per_unit')
    supplier_dis = fields.Float("Supplier Dis %")
    customs = fields.Float("customs %")
    sales_tax = fields.Float("Sales Tax %")
    total_qty_line = fields.Float("Total Qty")
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)

    @api.depends('qty', 'cost_subtotal', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            total_tax = 0
            if line.tax_ids:
                for tax in line.tax_ids:
                    total_tax += (line.cost_subtotal * tax.amount / 100)
            line.price_subtotal = line.cost_subtotal + total_tax

    @api.depends('qty', 'waste', 'cost_unit')
    def _compute_cost_per_unit(self):
        for line in self:
            line.cost_per_unit = line.qty * line.cost_unit
            line.waste_cost = line.cost_per_unit * line.waste / 100

    @api.onchange('total_qty_line', 'job_id.qty')
    def _onchange_total_qty_line(self):
        if self.total_qty_line > 0 and self.job_id.qty > 0:
            self.qty = self.total_qty_line / self.job_id.qty

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('waste', 'qty')
    def _get_planned_cost(self):
        for rec in self:
            rec.planned_qty = ((rec.waste / 100) * rec.qty) + rec.qty

    @api.depends('total_qty', 'cost_unit', 'ratio')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.total_qty * rec.cost_unit * rec.ratio

    @api.depends('planned_qty', 'job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.depends('planned_qty', 'cost_unit', 'currancy_id', 'ratio', 'supplier_dis', 'customs', 'sales_tax')
    def _compute_sub_total(self):
        for rec in self:
            amount = 0
            amount = rec.ratio * rec.cost_unit * rec.planned_qty
            supplier_dis = customs = sales_tax = 0
            rec.cost_subtotal_before_discount = rec.ratio * rec.cost_unit * rec.planned_qty
            if rec.supplier_dis:
                supplier_dis = ((rec.supplier_dis / 100) * amount)
            if rec.customs:
                customs = ((rec.customs / 100) * amount)
            if rec.sales_tax:
                sales_tax = ((rec.sales_tax / 100) * amount)
            rec.cost_subtotal = amount - supplier_dis + customs + sales_tax

    @api.onchange('currancy_id')
    def onchange_currancy_id(self):
        if self.currancy_id and self.job_id.project_id:
            # if self.job_id.job_template:
            #     self.ratio = self.job_id.job_template.currancy_id if self.job_id.job_template.currancy_id else 1

            if self.job_id.project_id.currancy_ids:
                if self.job_id.project_id.currancy_ids.search([('currancy_id', '=', self.currancy_id.id)], limit=1):
                    currancy_id = self.env['project.currency'] \
                        .search(
                        [('currancy_id', '=', self.currancy_id.id), ('project_id', '=', self.job_id.project_id.id)])
                    self.ratio = currancy_id.ratio if currancy_id else 1


class labour(models.Model):
    _name = "construction.labour"
    product_id = fields.Many2one("product.product", string="Product", required=True, \
                                 domain=[('labour', '=', True), ])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty", default=1)
    cost_unit = fields.Float(string="Cost/unit", required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total', string='price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value', string='Total Value')
    name = fields.Char(related='product_id.name')
    item = fields.Many2one(related='job_id.item', string='Item')
    active = fields.Boolean(default=True)

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.total_qty * rec.cost_unit

    @api.depends('planned_qty', 'job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.depends('planned_qty', 'cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal = rec.cost_unit * rec.planned_qty


class expense(models.Model):
    _name = "construction.expense"

    product_id = fields.Many2one("product.product", string="Product", required=True, \
                                 domain=[('expense', '=', True), ])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty", default=1)
    cost_unit = fields.Float(string="Cost/unit", required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total', string='price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value', string='Total Value')
    item = fields.Many2one(related='job_id.item', string='Item')
    active = fields.Boolean(default=True)

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.total_qty * rec.cost_unit

    @api.depends('planned_qty', 'job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.depends('planned_qty', 'cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal = rec.cost_unit * rec.planned_qty


class Subconstractor(models.Model):
    _name = "construction.subconstractor"
    name = fields.Char(compute='_get_name')
    product_id = fields.Many2one("product.product", string="Product", required=True,
                                 domain=[('subContractor', '=', True)])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty", default=1)
    cost_unit = fields.Float(string="Cost/unit", required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total', string='price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value', string='Total Value')
    tender_id = fields.Many2one(related='job_id.tender_id', store=True, index=True)
    item = fields.Many2one(related='job_id.item', string='Item')
    active = fields.Boolean(default=True)

    @api.depends('product_id', 'job_id')
    def _get_name(self):
        for rec in self:
            name = ''
            if rec.product_id:
                name += rec.product_id.name
            # if rec.job_id.project_id:
            #     name+=rec.job_id.project_id.name
            rec.name = name

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.total_qty * rec.cost_unit

    @api.depends('planned_qty', 'job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.depends('planned_qty', 'cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal = rec.cost_unit * rec.planned_qty


class Equpment(models.Model):
    _name = "construction.equipment"
    product_id = fields.Many2one("product.product", string="Product", \
                                 required=True, domain=[('equipment', '=', True), ])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty", default=1)
    cost_unit = fields.Float(string="Cost/unit", required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total', string='price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value', string='Total Value')
    item = fields.Many2one(related='job_id.item', string='Item')
    active = fields.Boolean(default=True)

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.total_qty * rec.cost_unit

    @api.depends('planned_qty', 'job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.depends('planned_qty', 'cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal = rec.cost_unit * rec.planned_qty
