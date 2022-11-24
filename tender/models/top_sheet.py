from odoo import fields, models, api

from odoo.exceptions import ValidationError


class Topsheet(models.Model):
    _name = 'top.sheet'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    project_id = fields.Many2one("project.project", required=True)
    lines_ids = fields.One2many("top.sheet.lines", "top_id", string="Lines")
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
            rec.total_value=0
            for line in rec.lines_ids:
                rec.total_value+=line.price


    @api.constrains('project_id')
    def get_projects(self):
        project_id = self.env['top.sheet'].search([('project_id', '=', self.project_id.id) \
                                                      ,  ('state', '!=', 'cancel')])

        if len(project_id) > 1:
            raise ValidationError("top sheet must be unique bar project")

    def action_confirm(self):
        self.state = 'confirm'
        value = self.refersh_cost()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", value)
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

    def refersh_cost(self):
        if self.split_method=='equal':
            cost=0
            total_indirect_cost = sum(self.lines_ids.mapped('price'))

            return total_indirect_cost/len(self.project_id.tender_ids.filtered(lambda line: line.display_type ==False))
        # if self.split_method=='qty':
        #     total_qty = 0
        #     total_qty = sum(self.project_id.tender_ids.mapped('qty'))
        #     for rec in self.tender_ids:
        #         rec.prec=round(((rec.tender_id.qty/total_qty)*100),2)
        #         rec.price=round(((rec.tender_id.qty/total_qty)),2)*self.top_id.total_value
        if self.split_method=='cost':
            total_value = 0
            total_value = sum(self.project_id.tender_ids.mapped('total_value'))
            return total_value


    # def create_indirect_cost(self):
    #     indirect_cost_id = self.env['indirect.cost']
    #     tender_ids=[]
    #     for rec in self.project_id.tender_ids:
    #         tender_ids.append((0,0,{
    #             'tender_id':rec.id
    #         }))
    #     indirect_cost_id.create({
    #         'top_id':self.id,
    #         'project_id':self.project_id.id,
    #         'split_method':self.split_method,
    #         'tender_ids':tender_ids,
    #
    #     })
    #     self.is_direct=True
    #     indirect_cost_id.refersh_cost()
    # def action_view_indirect_cost(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Indirect Cost ',
    #         'view_mode': 'tree,form',
    #         'res_model': 'indirect.cost',
    #         'domain': [('top_id', '=', self.id)],
    #         'target': 'current',
    #
    #     }

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError("You cann't delete confirmed sheet")
        res = super(Topsheet, self).unlink()

        return res



class TopSheetLines(models.Model):
    _name = 'top.sheet.lines'
    top_id = fields.Many2one("top.sheet")
    product_id = fields.Many2one("product.product",domain="[('detailed_type','=','service')]", required=True)

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

