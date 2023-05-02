from odoo import fields, models, api

from odoo.exceptions import ValidationError


class RiskFactor(models.Model):
    _name = "risk.factor"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    project_id = fields.Many2one("project.project", required=True)
    lines_ids = fields.One2many("risk.factor.lines", "top_id", string="Lines")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')],default='draft')
    total_value = fields.Float(compute='get_total_value_lines',string="Total Value")
    split_method = fields.Selection([('equal','Equal'),('cost','Cost')],default='equal')
    is_direct = fields.Boolean()
    total_direct_indirect = fields.Float(compute='get_total_direct_indirect',string="Total Cost")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('project_id')
    def get_total_direct_indirect(self):
        for rec in self:
            total_direct_indirect=0
            if rec.project_id:
                total_direct_indirect+=rec.project_id.total_value
                indirec_id = self.env['indirect.cost'].search([('project_id','=',rec.project_id.id)\
                                                                  ,('state','=','confirm')])
                total_direct_indirect+=indirec_id.total

            rec.total_direct_indirect=total_direct_indirect

    @api.depends('lines_ids.price')
    def get_total_value_lines(self):
        for rec in self:
            rec.total_value = 0
            for line in rec.lines_ids:
                rec.total_value += line.price

    @api.constrains('project_id')
    def get_projects(self):
        project_id = self.env['risk.factor'].search([('project_id', '=', self.project_id.id) \
                                                      ,  ('state', '!=', 'cancel')])

        if len(project_id) > 1:
            raise ValidationError("top sheet must be unique bar project")

    def action_confirm(self):
        if self.lines_ids.price < self.lines_ids.product_id.minimum_profit_amount:
            raise ValidationError(f"The minimum profit is  { self.lines_ids.product_id.minimum_profit_amount} !!!")
        elif self.lines_ids.prec < self.lines_ids.product_id.minimum_profit_percent:
            raise ValidationError(f"The minimum profit % is {self.lines_ids.product_id.minimum_profit_percent} !!!")
        else:
            self.state = 'confirm'
            value = self.refersh_cost()
            if self.split_method == 'equal':
                for rec in self.project_id.tender_ids:
                    if rec.display_type == False:
                        rec.profit = value
            if self.split_method == 'cost':
                total_indirect_cost = sum(self.lines_ids.mapped('price'))
                for rec in self.project_id.tender_ids:
                    if rec.display_type == False:
                        # rec.prec = round(((rec.total_value / value) * 100), 2)
                        rec.profit = (rec.total_value / self.project_id.total_value) * total_indirect_cost
            self.project_id.top_sheet_id=self.id

    def action_cancel(self):
        self.state = 'cancel'
        for rec in self.project_id.tender_ids:
            if rec.display_type == False:
                rec.profit = 0

    def refersh_cost(self):
        if self.split_method=='equal':
            cost=0
            total_indirect_cost = sum(self.lines_ids.mapped('price'))

            return total_indirect_cost/len(self.project_id.tender_ids.filtered(lambda line: line.display_type ==False))

        if self.split_method=='cost':
            total_value = 0
            total_value = sum(self.project_id.tender_ids.mapped('total_value'))
            return total_value


    def unlink(self):
        if self.state != 'draft':
            raise ValidationError("You cann't delete confirmed sheet")
        res = super(RiskFactor, self).unlink()

        return res


class RiskFactorLines(models.Model):
    _name = "risk.factor.lines"
    top_id = fields.Many2one("risk.factor")
    product_id = fields.Many2one("product.product",domain="[('risk_factor','=',True),('detailed_type','=','service')]", required=True)

    prec = fields.Float()
    price = fields.Float()
    total_direct_indirect = fields.Float(related='top_id.total_direct_indirect')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('price')
    def onchange_price(self):
        if self.price > 0 and self.total_direct_indirect:
            self.prec = ((self.price / self.total_direct_indirect) * 100)

    @api.onchange('prec')
    def onchange_prec(self):
        if self.prec > 0 and self.total_direct_indirect > 0:
            other_price = (self.prec * self.total_direct_indirect) / 100

            if other_price != self.price:
                 self.price = ((self.prec * self.total_direct_indirect) / 100)

