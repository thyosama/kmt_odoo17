from odoo import models,fields,api


class SalesOrder(models.Model):
    _name = 'construction.sale.order'
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
                amount_before_dis+=(rec.price_unit * rec.qty)
                total_discount += (rec.price_unit * rec.qty) - rec.total_value
            record.amount_before_dis=  amount_before_dis
            record.total_discount= total_discount

    @api.depends("amount_before_dis", "discount_lines")
    def _get_total_value(self):
        for record in self:
            record.total = record.discount_lines +record.amount_before_dis














class SalesOrderLine(models.Model):
    _name = 'construction.sale.order.line'
    code = fields.Char("Code")
    sale_id = fields.Many2one("construction.sale.order")
    item = fields.Many2one('product.item', string='Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity")
    notes = fields.Char("Notes")
    price_unit = fields.Float("Price Unit ")
    discount = fields.Float("Discount % ", )
    total_value = fields.Float("Total value ", compute='_get_total_value', store=True, index=True)
    type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')], string='Type', default='main')
    tender_id = fields.Many2one('construction.tender', string="Tender ID")
    sub_type = fields.Selection(related='tender_id.type', string='Type')

    @api.depends("price_unit", "qty","discount")
    def _get_total_value(self):
        for rec in self:
            value =rec.price_unit * rec.qty
            rec.total_value = (value)-(value*(rec.discount/100))
