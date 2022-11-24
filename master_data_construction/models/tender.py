from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class Tender(models.Model):
    _name = 'construction.tender'
    _rec_name = 'code'
    _order = 'id asc'
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    name = fields.Text(required=True,string="description")
    project_id = fields.Many2one("project.project", string="Project")
    code = fields.Char("Code")
    # type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')], string='Type', default='main')
    item = fields.Many2one('product.item', string='Item')
    # parent_item = fields.Many2one('construction.tender', string='Parent Item')
    # description = fields.Text("Description")
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    qty = fields.Float("Quantity")
    # status = fields.Selection([('main', 'Main'), ('renew', 'Renewal')], string="Status", default='main')
    notes = fields.Char("Notes")
    state = fields.Selection([('main', 'Main'), ('job_cost', 'Break Down'), \
                              ('job_estimate', 'Break Down Estimate')],
                             string="State", default="main")
    price_unit = fields.Float("Cost Unit ")
    total_value = fields.Float("Total value ", compute='_get_total_value', store=True, index=True)
    # lines_id = fields.One2many("construction.tender.line", 'parent_item')
    related_job = fields.Many2one("tender.related.job")
    tax_id = fields.Many2one("account.tax")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    indirect_cost = fields.Float()
    profit = fields.Float()
    sequence = fields.Integer(string='Sequence', default=10)
    sale_price = fields.Float(compute='calculate_sales_price')


    @api.depends('profit','indirect_cost','total_value')
    def calculate_sales_price(self):
        for rec in self:
            rec.sale_price=rec.profit+rec.indirect_cost+rec.total_value
    @api.onchange('item')
    def onchange_method(self):
        self.name = self.item.name
        self.related_job = self.item.related_job.id if self.item.related_job.id else ''

    @api.model
    def create(self,vals):
        res = super(Tender, self).create(vals)
        if res.project_id:
            lines = self.env['construction.tender'].search([
                ('project_id', '=', res.project_id.id),
                ('code', '=', res.code),
                ('id', '!=', res.id),
            ], limit=1)

            if lines and res.code:
                raise ValidationError(_("Code [ %s ] Already Exist") % (res.code))
        return res



    # def name_get(self):
    #     result = []
    #     for record in self:
    #         # result.append((record.id, "{} ({})".format(record.code, record.description)))
    #         result.append((record.id, "{}".format(record.description)))
    #
    #     return result
    @api.depends("price_unit", "qty")
    def _get_total_value(self):
        for rec in self:
            rec.total_value = rec.price_unit * rec.qty



    def save_lines(self):
        for rec in self.lines_id:
            if rec.tender_id:
                rec.tender_id.write({
                    'code':rec.code,
                    'item' : rec.item.id,
                    'description' : rec.description,
                    'qty' : rec.qty,
                })
            else:
                tender_id =self.env['construction.tender'].create({
                    'code': rec.code,
                    'item': rec.item.id,
                    'description': rec.description,
                    'qty': rec.qty,

                })
                rec.tender_id = tender_id.id


class Child(models.Model):
    _name = 'construction.tender.line'
    code = fields.Char("Code")
    item = fields.Many2one('product.item', string='Item')
    tender_id = fields.Many2one('construction.tender', string='Tender')
    description = fields.Text("Description")
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    qty = fields.Float("Quantity")

    notes = fields.Char("Notes")




    # _sql_constraints = [
    #     ('code_uniq', 'UNIQUE (code)', 'You can not have  the same code !')
    # ]

    def unlink(self):
        if self.tender_id:
            self.tender_id.unlink()
        return super(Child, self).unlink()

    # @api.constrains('code')
    # @api.onchange('code')
    # def constrains_code(self):
    #     if self.parent_item:
    #         lines = self.env['construction.tender'].search([
    #             ('id', '=', self._origin.parent_item.id),
    #             ('code', '=', self.code),
    #             ('id', '!=', self._origin.id),
    #         ], limit=1)
    #         if lines and self.code:
    #             raise ValidationError(_("Code [ %s ] Already Exist") % (self.code))
