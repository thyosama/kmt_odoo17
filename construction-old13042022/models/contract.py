from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
class contract(models.Model):
    _name = 'construction.contract'
    name = fields.Char("Name",compute='_get_name')
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type", default='owner')
    project_id = fields.Many2one("project.project", string="Project")
    parner_id = fields.Many2one(related="project_id.partner_id", string="Customer", store=True, index=True)
    date = fields.Date("Date", default=datetime.today())
    recieve_date = fields.Date("Receive Date")
    contract_id = fields.Many2one("construction.contract.user", string="Contract",domain="[('type','=',type)]")
    account_id = fields.Many2one(related="contract_id.account_id",string="Partner Account", store=True, index=True)
    order_id = fields.Many2one("construction.sale.order", string="Referance Financial Offer")
    down_payment_prectenge = fields.Float("Down Payment %")
    down_payment_value = fields.Float("Down Payment Value", compute="calculate_down_payment",
                                      store=True, index=True)
    revenue_account_id = fields.Many2one(related='contract_id.counterpart_account_id',store=True,index=True, string="Revenue Account")
    lines_id = fields.One2many("construction.contract.line", "contract_id",compute='_onchnage_project',store=True,index=1,readonly=False)
    sub_lines_id = fields.One2many("construction.contract.line", "sup_contract_id")

    total_value = fields.Float(compute='_get_total_value',string="Contract Value")
    deduction_ids = fields.One2many("contract.deduction.allowance.lines","contract_id",
                                     string="Deductions",domain=[('type','=','deduction')])
    allowance_ids = fields.One2many("contract.deduction.allowance.lines","contract_id",
                                     string="Allowance",domain=[('type','=','addition')])

    sub_contactor = fields.Many2one("res.partner",string="sub contractor Name")
    date = fields.Date("Date", default=datetime.today())
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default='draft')
    number_of_invoice = fields.Integer("Number Of Invoice")



    @api.depends('create_date')
    def _get_name(self):

        for rec in self:
            if rec.type=='owner':
                rec.name= 'Owner Contract  /'+str(rec.project_id.name) +" /"+str(rec.id).zfill(4)
            elif rec.type=='supconstractor':
                rec.name =  str(rec.project_id.name) +"/"+rec.sub_contactor.name+" /"+str(rec.id).zfill(4)
    @api.depends('lines_id')
    def _get_total_value(self):
        for rec in self:
            rec.total_value =0
            if rec.type=='owner':
                for record in rec.lines_id:
                    rec.total_value+=record.total_value
            elif rec.type=='supconstractor':
                for record in rec.sub_lines_id:
                    rec.total_value+=record.total_value

    @api.depends('down_payment_prectenge','total_value')
    def calculate_down_payment(self):
        for rec in self:
            rec.down_payment_value = (rec.down_payment_prectenge/100)*rec.total_value


    @api.depends("project_id")
    def _onchnage_project(self):

        if self.project_id:
            order_id= self.env['construction.sale.order'].search([('project_id', '=', self.project_id.id),
                                                                  ('state','=','confirm')], limit=1)
            lines = []
            for rec in self.lines_id:
                rec.unlink()
            if order_id:
                self.order_id =order_id
                for rec in self.order_id.order_lines:
                    lines.append((0,0, {
                                   'code' : rec.code,
                                  'item' : rec.item.id,
                                  'description': rec.description,
                                  'qty' : rec.qty,
                                  'notes': rec.notes,'sub_type':rec.type,
                                  'price_unit' : rec.price_unit, 'discount':rec.discount,
                                   'type':'owner','tender_id':rec.tender_id.id

                                  }))

                if self.type=='owner':
                    self.lines_id = lines
            else:
                self.order_id = ''
                for rec in self.lines_id:
                    rec.unlink()
    def action_confirm(self):
        self.state='confirm'



class ContractLine(models.Model):
    _name = 'construction.contract.line'
    code = fields.Char("Code")
    contract_id = fields.Many2one("construction.contract")
    sup_contract_id = fields.Many2one("construction.contract")
    item = fields.Many2one('product.item', string='Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    qty = fields.Float("Quantity")
    notes = fields.Char("Notes")
    price_unit = fields.Float("Price Unit ", )
    discount = fields.Float("Discount % ", )
    total_value = fields.Float("Total value ", compute='_get_total_value', store=True, index=True)
    sub_type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')], string='Type', default='main')
    sub_contarctor_item = fields.Many2one('construction.subconstractor',string="SubConstractor")
    tender_id = fields.Many2one('construction.tender',string="Tender ID")
    wbs_item = fields.Many2one('wbs.item.line',string="WBS-item")
    type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type", default='owner')

    @api.onchange('wbs_item')
    def get_qty_price(self):
        if self.wbs_item and self.tender_id:
            wbs_id = self.env['wbs.distribution.line'].search([('tender_id','=',self.tender_id.id),
                                                               ('item_wbs','=',self.wbs_item.id)],limit=1)

            self.qty = wbs_id.qty_item
    @api.onchange('tender_id')
    def _get_tender_ids(self):

        if self.sup_contract_id.project_id:

            domain = {'tender_id': [('type','=','transcation'),('id', 'in', self.sup_contract_id.project_id.tender_ids.ids)]
                      }
            return {'domain': domain}
        elif self.contract_id.project_id:

                domain = {'tender_id': [('type', '=', 'transcation'),
                                        ('id', 'in', self.contract_id.project_id.tender_ids.ids)]
                    }

                return {'domain': domain}


    # @api.onchange('sub_contarctor_item')
    # def _get_sub_contarctor_item_ids(self):
    #     if self.sub_contarctor_item:
    #         self.qty = self.sub_contarctor_item.planned_qty




    @api.onchange('item')
    def get_item_at_project(self):
        if self.contract_id.project_id:
            item = self.env['construction.tender'].search([('project_id','=',self.contract_id.project_id.id)])
            ids=[]
            for rec in item.item:
                ids.append(rec.id)
            domain = {'item': [('id','in',ids)]}


            return {'domain': domain}


    @api.depends("price_unit", "qty", "discount")
    def _get_total_value(self):
        for rec in self:
            value = rec.price_unit * rec.qty
            rec.total_value = (value) - (value * (rec.discount / 100))

    @api.onchange('sub_contarctor_item','tender_id')
    def _onchange_tender_id(self):


        if self.tender_id or self.sub_contarctor_item:

            sub_contractors = []
            job_cost_id = self.env['construction.job.cost'].search([
                ('project_id', '=', self.sup_contract_id.project_id.id),
                ('tender_id', '=', self.tender_id.id),
            ])

            for job_cost in job_cost_id:
                # print(job_cost, "Line", job_cost.subconstractor_ids)
                for line in job_cost.subconstractor_ids:
                    sub_contractors.append(line.id)
            job_id = self.env['construction.job.cost'].search([('tender_id', '=', self.tender_id.id)], limit=1)
            if job_id and self.sub_contarctor_item:
                sub_con = self.env['construction.subconstractor'].search(
                    [('job_id', '=', job_id.id), ('id', '=', self.sub_contarctor_item.id)], limit=1)
                self.price_unit = sub_con.cost_unit
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>0",job_cost_id,sub_contractors)

            return {'domain': {'sub_contarctor_item': [('id', 'in', sub_contractors)]}}


    @api.onchange('wbs_item')
    def get_wbs_id(self):
        webs=[]
        if self.contract_id:
         webs = self.env['wbs.item'].search([('name', '=', self.contract_id.project_id.id)])
        if self.sup_contract_id:

            webs = self.env['wbs.item'].search([('name', '=', self.sup_contract_id.project_id.id)])
        ids = []

        if webs:
            for rec in webs.item_ids:
                ids.append(rec.id)
            domain = {'wbs_item': [('id', 'in', ids)]}

            return {'domain': domain}
    @api.model
    def create(self,vals):
        res = super(ContractLine, self).create(vals)
        if 'code' in vals:
            res.tender_id = self.env['construction.tender'].search([('code', '=', res.code),
                                                                     ('project_id', '=',
                                                                      res.contract_id.project_id.id)])
        if res.contract_id.type=='supconstractor':
            res.code = self.env['construction.tender'].search([('id', '=', res.tender_id.id),
                                                                    ('project_id', '=',
                                                                     res.contract_id.project_id.id)])

        return  res