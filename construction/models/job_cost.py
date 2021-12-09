from odoo.exceptions import ValidationError

from odoo import models, fields, api
from datetime import datetime

class Tender(models.Model):
    _name = 'construction.job.cost'
    name = fields.Char(compute='get_name')
    project_id = fields.Many2one("project.project",string = "Project")
    code = fields.Char("Code")
    type = fields.Selection([('main','Main'),('transcation','Transcation')],string ='Type',default='main')
    item = fields.Many2one('product.item',string ='Item')
    parent_item = fields.Many2one('product.item',string ='Parent Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one(related='item.uom_id',string="Unit of Measure")
    qty = fields.Float("Quantity")
    status = fields.Selection([('main','Main'),('renew','Renewal')],string="Status",default='main')
    notes = fields.Char("Notes")
    tender_id = fields.Many2one("construction.tender")
    date = fields.Date("Date",default=datetime.today())
    start_date = fields.Date("Start Date",default=datetime.today())
    end_date = fields.Date("End Date")
    dif = fields.Char("Differance Date", compute='_get_dif')
    partner_id = fields.Many2one("res.partner","Customer")

    material_ids = fields.One2many('construction.material',"job_id")
    total_material = fields.Float(compute='_compute_total_material',string="Total Material",store=True,index=True)
    labour_ids = fields.One2many('construction.labour',"job_id")
    total_labour = fields.Float(compute='_compute_total_labour',string="Total Labours",store=True,index=True)
    expense_ids = fields.One2many('construction.expense',"job_id")
    total_expense = fields.Float(compute='_compute_total_expense',string="Total Expenses",store=True,index=True)
    subconstractor_ids = fields.One2many('construction.subconstractor',"job_id")
    total_subconstractor = fields.Float(compute='_compute_total_subconstractor',string="Total Subconstractors",store=True,index=True)
    equipment_ids = fields.One2many('construction.equipment',"job_id")
    total_equipment = fields.Float(compute='_compute_total_equipment',string="Total Equipment",store=True,index=True)
    total_value_all = fields.Float(compute='_compute_all_values',string="Total",store=True,index=True)
    is_template = fields.Boolean(default=False)
    job_template = fields.Many2one('construction.job.cost',string="Break Down Template",domain="[('is_template','=',True)]")
    indirect_type = fields.Selection([('percentage','Percentage'),('amount','Amount')],string="Indirect Type",default="percentage")
    profit_type = fields.Selection([('percentage','Percentage'),('amount','Amount')],string="Profit Type",default="percentage")
    indirect_percentage = fields.Float("Indirect Cost Percentage")
    indirect_amount = fields.Float("Indirect Cost Amount",compute='_get_indirect_amount_prectage',store=True,index=True)
    tax_percentage = fields.Float("Tax Value Percentage")
    tax_amount = fields.Float("Tax Value Amount",compute="_get_mount_tax",store=True,index=True)
    profit_percentage = fields.Float("Profit Percentage",compute="_get_profit_amount_prectage",store=True,index=True)
    profit_amount = fields.Float("Profit Amount",compute="_get_profit_amount_prectage",store=True,index=True)
    value_indirect = fields.Float("Value",compute='_get_total_indirect_value',store=True,index=True)
    gross_profit = fields.Float("Gross Value",compute='_get_total_gross_value',store=True,index=True)
    sales_price = fields.Float("Sales Price",compute='_get_total_sale_price',store=True,index=True)
    state = fields.Selection([('draft','draft'),('confirm','Confirm'),('approve','Approve'),
                              ('quotation','Financial Offer')],string="State",default="draft")
    sales_price_update = fields.Float("Sales Price")
    name2 = fields.Char("Name")


    @api.depends('code','project_id','name2')
    def get_name(self):
        for rec in self:
            name=''
            if rec.project_id:
                name+=rec.project_id.name+"/"
            if rec.description:
                name+=rec.description+"/"
            if rec.code:
                name+=rec.code
            if rec.name2:
                name=rec.name2
            rec.name=name

    def action_confirm(self):
        self.state = 'confirm'



    def action_approve(self):
        self.state = 'approve'
        self.tender_id.state = 'job_estimate'
        self.tender_id.price_unit = self.sales_price

    def action_quotation(self):
        self.state = 'quotation'
        #self.project_id.create_quotation()

    @api.depends("gross_profit","tax_amount")
    def _get_total_sale_price(self):
        self.sales_price =0
        for rec in self:
            rec.sales_price = rec.gross_profit+rec.tax_amount
            rec.tender_id.price_unit = rec.sales_price


    @api.depends("profit_amount", "value_indirect")
    def _get_total_gross_value(self):
        self.gross_profit = 0
        for rec in self:
            if rec.profit_type == 'percentage':
                rec.profit_amount = rec.value_indirect * (rec.profit_percentage / 100)
            elif rec.profit_type == 'amount' :
                rec.profit_percentage = (rec.profit_amount * 100) / rec.value_indirect
            rec.gross_profit = rec.value_indirect + rec.profit_amount


    @api.depends("tax_percentage","gross_profit")
    def _get_mount_tax(self):
        for rec in self:
            rec.tax_amount = (rec.gross_profit/(1-(rec.tax_percentage / 100))) - rec.gross_profit




    @api.depends("indirect_type","indirect_percentage","indirect_amount","total_value_all")
    def _get_indirect_amount_prectage(self):
        for rec in self:

            if rec.indirect_type=='percentage':
                rec.indirect_amount = rec.total_value_all *(rec.indirect_percentage/100)
            elif rec.indirect_type == 'amount' :
                rec.indirect_percentage = (rec.indirect_amount*100)/rec.total_value_all

    @api.onchange("indirect_type", "indirect_percentage", "indirect_amount", "total_value_all")
    def _onchange_indirect_amount_prectage(self):
        for rec in self:
            if rec.indirect_type == 'percentage':
                rec.indirect_amount = rec.total_value_all * (rec.indirect_percentage / 100)
            elif rec.indirect_type == 'amount':
                rec.indirect_percentage = (rec.indirect_amount * 100) / rec.total_value_all

    @api.depends("indirect_amount", "total_value_all", "indirect_percentage")
    def _get_total_indirect_value(self):

        for rec in self:
            if rec.indirect_type == 'percentage':
                rec.indirect_amount = rec.total_value_all * (rec.indirect_percentage / 100)
            elif rec.indirect_type == 'amount':
                rec.indirect_percentage = (rec.indirect_amount * 100) / rec.total_value_all
            rec.value_indirect = rec.total_value_all + rec.indirect_amount
    @api.depends("profit_type", "profit_percentage", "profit_amount", "total_value_all")
    def _get_profit_amount_prectage(self):
        for rec in self:
            if rec.profit_type == 'percentage':
                rec.profit_amount = rec.value_indirect * (rec.profit_percentage / 100)
            elif rec.profit_type == 'amount':
                rec.profit_percentage = (rec.profit_amount * 100) / rec.value_indirect

    @api.onchange("profit_type", "profit_percentage", "profit_amount", "total_value_all")
    def _onchange_profit_amount_prectage(self):
        for rec in self:
            if rec.profit_type == 'percentage':
                rec.profit_amount = rec.value_indirect * (rec.profit_percentage / 100)
            elif rec.profit_type == 'amount' :
                rec.profit_percentage = (rec.profit_amount * 100) / rec.value_indirect



    @api.onchange('job_template')
    def _get_job_template(self):
        values=[]
        for rec in self.job_template:
            if rec.material_ids:
                for mat in rec.material_ids:

                    values.append((0,0,{
                        'product_id':mat.product_id.id,
                        'description':mat.description,
                        'uom_id':mat.uom_id.id,'qty':mat.qty,
                        'waste':mat.waste,'cost_unit':mat.cost_unit

                    }))

                self.material_ids = values
            if rec.labour_ids:
                values=[]

                for lab in rec.labour_ids:
                    values.append((0,0,{
                        'product_id': lab.product_id.id,
                        'description': lab.description,
                        'uom_id': lab.uom_id.id, 'planned_qty': lab.planned_qty,
                        'cost_unit': lab.cost_unit

                    }))
                self.labour_ids = values

            if rec.expense_ids:
                values=[]

                for exp in rec.expense_ids:
                    values.append((0, 0, {
                        'product_id': exp.product_id.id,
                        'description': exp.description,
                        'uom_id': exp.uom_id.id, 'planned_qty': exp.planned_qty,
                        'cost_unit': exp.cost_unit

                    }))
                self.expense_ids =values
            if rec.subconstractor_ids:
                values=[]
                for sub in rec.subconstractor_ids:
                    values.append((0, 0, {
                        'product_id': sub.product_id.id,
                        'description': sub.description,
                        'uom_id': sub.uom_id.id, 'planned_qty': sub.planned_qty,
                        'cost_unit': sub.cost_unit

                    }))
                self.subconstractor_ids = values
            if rec.equipment_ids:
                values=[]
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
        if self.start_date and self.end_date and  self.end_date < self.start_date:
            raise ValidationError("End Date Must be greater than Start Date")

    @api.constrains("end_date")
    def _check_end_date(self):
        if self.start_date and  self.end_date and self.end_date < self.start_date:
            raise ValidationError("End Date Must be greater than Start Date")

    @api.depends('start_date','end_date')
    def _get_dif(self):
        self.dif =''
        for rec in self:
            dif =''
            if rec.start_date and rec.end_date:
                self.dif = rec.end_date - rec.start_date
    @api.depends('total_material','total_labour','total_expense','total_subconstractor','total_equipment')
    def _compute_all_values(self):
        for rec in self:
            self.total_value_all = \
                rec.total_material+rec.total_labour+rec.total_expense+rec.total_subconstractor+rec.total_equipment

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

    @api.depends('material_ids')
    def _compute_total_material(self):
        self.total_material =0
        for record in self:
          for rec in record.material_ids:
            record.total_material += rec.cost_subtotal
    def update_sales_price(self):


        view_form = self.env.ref('construction.view_job_cost_fromm_update')

        return {
            'name': ('Update'),
            'view_mode': 'form',
            'view_type': 'form',
            'views': [ (view_form.id, 'form')],
            'res_model': 'construction.job.cost',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id':self.id,
        }
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
    def update_price(self):
        self.indirect_amount = 0
        self.indirect_percentage = 0
        self.profit_type = 'amount'

        self.profit_amount = self.sales_price_update-self.total_value_all
        # self.gross_profit = self.sales_price_update-self.total_value_all
        self.sales_price = self.sales_price_update





class Material(models.Model):
    _name = 'construction.material'
    product_id = fields.Many2one("product.product",string="Product",required=True,domain=[('type','=','product')])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity",required=True)
    waste = fields.Float("Waste %")
    planned_qty = fields.Float("Planned Qty",default=1,compute='_get_planned_cost')
    cost_unit = fields.Float(string="Cost/unit",required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total',string = 'price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty',string = 'Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    item = fields.Many2one(related='job_id.item', string='Item')
    total_value = fields.Float(compute='_compute_total_value',string = 'Total Value')


    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
    @api.depends('waste','qty')
    def _get_planned_cost(self):
        for rec in self:
            rec.planned_qty = ((rec.waste/100)*rec.qty) + rec.qty
    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:

            rec.total_value = rec.total_qty * rec.cost_unit
    @api.depends('planned_qty','job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty*rec.job_id.qty
    @api.depends('planned_qty','cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal =  rec.cost_unit*rec.planned_qty




class labour(models.Model):
    _name = 'construction.labour'
    product_id = fields.Many2one("product.product",string="Product",required=True,domain=[('type','!=','product')])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty",default=1)
    cost_unit = fields.Float(string="Cost/unit",required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total',string = 'price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty',string = 'Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value',string = 'Total Value')
    name = fields.Char(related='product_id.name')
    item = fields.Many2one(related='job_id.item', string='Item')




    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:

            rec.total_value = rec.total_qty * rec.cost_unit
    @api.depends('planned_qty','job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty*rec.job_id.qty
    @api.depends('planned_qty','cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal =  rec.cost_unit*rec.planned_qty





class expense(models.Model):
    _name = 'construction.expense'

    product_id = fields.Many2one("product.product",string="Product",required=True,domain=[('type','!=','product')])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty",default=1)
    cost_unit = fields.Float(string="Cost/unit",required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total',string = 'price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty',string = 'Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value',string = 'Total Value')
    item = fields.Many2one(related='job_id.item', string='Item')


    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:

            rec.total_value = rec.total_qty * rec.cost_unit
    @api.depends('planned_qty','job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty*rec.job_id.qty
    @api.depends('planned_qty','cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal =  rec.cost_unit*rec.planned_qty







class Subconstractor(models.Model):
    _name = 'construction.subconstractor'
    name = fields.Char(compute='_get_name')
    product_id = fields.Many2one("product.product",string="Product",required=True,domain=[('type','!=','product')])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty",default=1)
    cost_unit = fields.Float(string="Cost/unit",required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total',string = 'price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty',string = 'Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value',string = 'Total Value')
    tender_id = fields.Many2one(related='job_id.tender_id',store=True,index=True)
    item = fields.Many2one(related='job_id.item', string='Item')

    @api.depends('product_id','job_id')
    def _get_name(self):
        for rec in self:
            name =''
            if rec.product_id:
                name+=rec.product_id.name
            # if rec.job_id.project_id:
            #     name+=rec.job_id.project_id.name
            rec.name =  name

    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:

            rec.total_value = rec.total_qty * rec.cost_unit
    @api.depends('planned_qty','job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty*rec.job_id.qty
    @api.depends('planned_qty','cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal =  rec.cost_unit*rec.planned_qty




class Equpment(models.Model):
    _name = 'construction.equipment'
    product_id = fields.Many2one("product.product",string="Product",required=True,domain=[('type','!=','product')])
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    planned_qty = fields.Float("Planned Qty",default=1)
    cost_unit = fields.Float(string="Cost/unit",required=True)
    cost_subtotal = fields.Float(compute='_compute_sub_total',string = 'price Cost sub total')
    total_qty = fields.Float(compute='_compute_total_qty',string = 'Total Quantity')
    job_id = fields.Many2one("construction.job.cost")
    total_value = fields.Float(compute='_compute_total_value',string = 'Total Value')
    item = fields.Many2one(related='job_id.item', string='Item')


    @api.onchange('product_id')
    def _get_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.depends('total_qty', 'cost_unit')
    def _compute_total_value(self):
        for rec in self:

            rec.total_value = rec.total_qty * rec.cost_unit
    @api.depends('planned_qty','job_id.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = rec.planned_qty*rec.job_id.qty
    @api.depends('planned_qty','cost_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.cost_subtotal =  rec.cost_unit*rec.planned_qty


