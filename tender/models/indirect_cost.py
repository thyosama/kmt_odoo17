from odoo import fields, models, api

from odoo.exceptions import ValidationError

class Inderict(models.Model):
    _name = 'indirect.cost'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    project_id = fields.Many2one("project.project", required=True)
    lines_ids = fields.One2many('indirect.cost.line',"indirect_id")
    split_method = fields.Selection([('equal', 'Equal'), ('cost', 'Cost')], default='equal')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')],default='draft')
    top_id = fields.Many2one("top.sheet",string="top Sheet")
    indirect_cost = fields.Float(related='project_id.total_value')
    total= fields.Float(compute='get_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('lines_ids')
    def get_total(self):
        for rec in self:
            rec.total=0
            if rec.lines_ids:
                rec.total=sum(rec.lines_ids.mapped('price'))




    @api.constrains('project_id')
    def get_projects(self):
        project_id = self.env['indirect.cost'].search([('project_id', '=', self.project_id.id) \
                                                      , ('state', '!=', 'cancel')])
        if len(project_id) > 1:
            raise ValidationError("direct Cost must be unique bar project")
    def action_confirm(self):
        self.state = 'confirm'
        value = self.refersh_cost()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",value)
        if self.split_method == 'equal':
            for rec in self.project_id.tender_ids:
                if rec.display_type == False:
                    rec.indirect_cost = value
        if self.split_method == 'cost':
            total_indirect_cost = sum(self.lines_ids.mapped('price'))
            for rec in self.project_id.tender_ids:
                if rec.display_type==False:
                    # rec.prec = round(((rec.total_value / value) * 100), 2)
                    rec.indirect_cost = ((rec.total_value / self.project_id.total_value)) * total_indirect_cost
        self.project_id.indirect_id=self.id
    def set_draft(self):
        self.state='draft'
    # @api.constrains('tender_ids')
    # def check_total(self):
    #     total=sum(self.tender_ids.mapped('price'))
    #     print("?>>>>>>>>>>>>>>>",total,self.top_id.total_value)
    #     if total-self.top_id.total_value!=0:
    #         raise ValidationError("total indirect cost must be equal total top sheet")
    def action_cancel(self):
        self.state = 'cancel'


    # split_method = fields.Selection([('equal', 'Equal'), ('qty', 'Quantity'), ('cost', 'Cost')], default='equal')

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

    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise ValidationError("You cann't delete confirmed Indirect Cost")
        res = super(Inderict, self).unlink()

        return res





class Lines(models.Model):
    _name = 'indirect.cost.line'
    product_id = fields.Many2one("product.product",domain="[('indirect_cost','=',True)]", required=True)
    indirect_id = fields.Many2one("indirect.cost")
    prec = fields.Float()
    price = fields.Float()
    indirect_cost = fields.Float(related='indirect_id.project_id.total_value')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    @api.onchange('price')
    def onchange_price(self):
        if self.price>0 and self.indirect_cost:
            self.prec= (self.price/self.indirect_cost)*100

    @api.onchange('prec')
    def onchange_prec(self):
        if self.prec>0 and self.indirect_cost>0:

            other_price = (self.prec * self.indirect_cost) /100

            if other_price!=self.price:

                self.price = (self.prec * self.indirect_cost) /100






