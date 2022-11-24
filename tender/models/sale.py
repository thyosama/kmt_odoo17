from odoo import models,fields,api


class SalesOrder(models.Model):
    _name = 'construction.sale.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name = fields.Char("name")
    project_id = fields.Many2one("project.project", string="Project")
    partner_id = fields.Many2one("res.partner", string="Customer")
    created_date = fields.Date("Created Date")
    order_lines = fields.One2many("construction.sale.order.line","sale_id")
    discount_lines = fields.Float("Discount")
    amount_before_dis = fields.Float(compute='_get_total_amount_dis',string="Total Amount Before Discount")
    total_discount = fields.Float(compute="_get_total_amount_dis",string="Total Discount")
    total = fields.Float(compute="_get_total_value",string="Total")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')],default="draft")
    active = fields.Boolean(default=True)
    version = fields.Char()
    version_num = fields.Integer()
    estimation_version = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)



    def action_round(self):
        for rec in self.order_lines:
            rec.price_unit=round(rec.price_unit)



    @api.onchange("discount_lines")
    def _onchnage_discount(self):
        for rec in self.order_lines:
            rec.discount = self.discount_lines


    def action_confirm(self):
        self.state="confirm"




    @api.depends("order_lines","order_lines.total_value")
    def _get_total_amount_dis(self):
        for record in self:
            record.amount_before_dis = 0
            record.total_discount =0
            amount_before_dis,total_discount=0,0
            for rec in record.order_lines:
                amount_before_dis+=(rec.price_unit )
                # total_discount += (rec.price_unit * rec.qty) - rec.total_value
            record.amount_before_dis=  amount_before_dis
            record.total_discount= 0

    @api.depends("amount_before_dis", "discount_lines")
    def _get_total_value(self):
        for record in self:
            record.total =  record.amount_before_dis-record.discount_lines














class SalesOrderLine(models.Model):
    _name = 'construction.sale.order.line'
    name = fields.Char("Code")
    sale_id = fields.Many2one("construction.sale.order")
    item = fields.Many2one('product.item', string='Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity")
    notes = fields.Char("Notes")
    price_unit = fields.Float("Sales Price ")
    discount = fields.Float("Discount % ", )
    total_value = fields.Float("Total value ")
    type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')], string='Type', default='main')
    tender_id = fields.Many2one('construction.tender', string="Tender ID")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    price = fields.Float("Price Unit",compute='get_price')

    @api.depends('price_unit','qty')
    def get_price(self):
        for rec in self:
            if rec.qty>0:
                rec.price=rec.price_unit/rec.qty
            else:
                rec.price=0


    # @api.depends("price_unit", "qty","discount")
    # def _get_total_value(self):
    #     for rec in self:
    #         value =rec.price_unit * rec.qty
    #         rec.total_value = (value)-(value*(rec.discount/100))
