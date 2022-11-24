from odoo import fields, models, api, _
import itertools

from odoo.exceptions import ValidationError


class Engineer(models.Model):
    _name = 'construction.engineer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    _description = 'engineer'

    name = fields.Char(default=_('New'))
    contract_id = fields.Many2one("construction.contract")
    type_move = fields.Selection([('process', 'Process'), ('final', 'Final')], string="Type", default='process')

    project_id = fields.Many2one("project.project")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], default='draft')
    lines = fields.One2many(
        comodel_name='construction.engineer.lines',
        inverse_name='parent_id',
        string='',
        required=False)
    referance = fields.Char()
    deduction_ids = fields.One2many("contract.deduction.allowance.lines", "eng_template_id",
                                    string="Deductions", domain=[('type', '=', 'deduction')])
    allowance_ids = fields.One2many("contract.deduction.allowance.lines", "eng_template_id",
                                    string="Allowance", domain=[('type', '=', 'addition')])

    def action_select_items(self):
        return {
            'name': (''),
            'view_mode': 'form',
            'res_model': 'template.items',
            'type': 'ir.actions.act_window',
            'context': {'default_template_id': self.id},
            'target': 'new'
        }



    def action_confirm(self):
        self.state = 'confirm'
        self.create_invoice()

    def action_cancel(self):
        self.state = 'cancel'

    def create_invoice(self):

        prev_invoice_ids = self.env['account.invoice'].search([ \
            ( 'type','=', 'owner'),('state','!=','cancel'),
            ('contract_id','=',self.contract_id.id)])
        check = False
        print(">>>>>>>>>>.",prev_invoice_ids)
        if prev_invoice_ids:
            check=True

        invoice = self.env['account.invoice'].create(
            {
                'type': 'owner',
                'type_move': self.type_move,
                'contract_id': self.contract_id.id,
                'eng_template_id': self.id,
                'invoice_line': self.get_lines(self.contract_id,check)

            }
        )
        for ded in self.allowance_ids:
            self.env['contract.addition.lines.invoice'].create({
                'type':ded.type,
                'sub_type':ded.sub_type,
                'name':ded.name.id,
                'account_id':ded.account_id.id,
                'is_precentage':ded.is_precentage,
                'precentage':ded.precentage,
                'invoice_id':invoice.id,

            })
        for ded in self.deduction_ids:
            self.env['contract.deduction.lines.invoice'].create({
                'type':ded.type,
                'sub_type':ded.sub_type,
                'name':ded.name.id,
                'account_id':ded.account_id.id,
                'is_precentage':ded.is_precentage,
                'precentage':ded.precentage,
                'invoice_id':invoice.id,

            })


    def get_lines(self, contract_id,check):

        tender = []

        # if check:
        #     return  tender
        for rec in self.lines:
            if rec.display_type==False:
                tender.append({
                    'id': rec.contract_line_id.id,
                    'contract_line_id': rec.contract_line_id.id,
                    'qty': rec.qty,
                    'price':rec.prec_price,
                    'last_qty':rec.previous_qty

                })
        lines = sorted(tender, key=lambda i: (i['id']))
        docs = []
        invoice_previous = self.env['account.invoice'].search([('contract_id', '=', contract_id.id)],
                                                              order='id desc', limit=1)


        for key, group in itertools.groupby(lines, key=lambda x: (x['id'])):

            i =last_qty= price=qty=0
            id = ''

            for item in group:
                i += item['qty']
                price += item['price']
                # last_qty += item['last_qty']

                id = item['id']
            invoicelines = self.env['account.invoice.line'].search(
                [('contract_line_id', '=', id), ('invoice_id', '=', invoice_previous.id), ])
            for l in invoicelines:
                print(">>>>>>>>>>>",l.quantity,l.percentage)
                last_qty+=(l.quantity)
            contract_line_id = self.env['construction.contract.line'].search([('id','=',id)])
            percentage = (price/contract_line_id.total_value)*100 if contract_line_id.total_value>0 else 0

            # print(">>>>>>>>>>>>>>>>",percentage,contract_line_id.qty*(percentage/100))
            docs.append((0, 0, {
                'contract_line_id': id,
                'current_qty':contract_line_id.qty*(percentage/100),
                'last_qty':last_qty,
                'code': contract_line_id.code,
                'item': contract_line_id.item.id,
                # 'price_unit':price,
                'price_unit':contract_line_id.price_unit,
                'percentage':percentage,
                'contract_qty':contract_line_id.qty,
                'name':contract_line_id.name,
            }))
        return docs

    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise ValidationError("You  Cann't delete ")
        res=super(Engineer, self).unlink()
        return res

    @api.model
    def create(self, vals):

        res = super(Engineer, self).create(vals)
        res.name = self.env['ir.sequence'].next_by_code(
            'construction.engineer')
        return res


class Engineerlines(models.Model):
    _name = 'construction.engineer.lines'
    _description = 'engineer'
    _order = 'name,item'
    sequence = fields.Integer(string='Sequence', default=10)
    parent_id = fields.Many2one("construction.engineer", ondelete='cascade', index=True, copy=False)

    tender_id = fields.Char(string="Tender ID")
    item = fields.Many2one('product.item',string='Item')
    name = fields.Text(string="Description")
    uom_id = fields.Many2one(related='item.uom_id', string="Unit of Measure")
    remind_qty = fields.Float("Remind Quantity")
    qty = fields.Float("Quantity")
    tender_qty = fields.Float(string="Contract Quantity")
    notes = fields.Char("Notes")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
    stage_id = fields.Many2one("contract.stage")
    percentage = fields.Float(string="percentage %",compute='get_percentage')
    related_job = fields.Many2one(related='item.related_job')
    prec_price = fields.Float("Price",compute='get_price_cost')
    other_prec = fields.Float("Prectenge stage")
    amount = fields.Float("Amount",compute='get_price_cost')
    contract_line_id  =fields.Many2one("construction.contract.line")
    previous_qty = fields.Float(compute="get_previous_qty")
    contract_id = fields.Many2one(related='parent_id.contract_id')

    @api.depends( 'item','stage_id','contract_id','parent_id.state')
    def get_previous_qty(self):
        for rec in self:
            rec.previous_qty=0
            if rec.id:
                lines_pre_ids = self.env['construction.engineer.lines'].search([('contract_id','=',rec.contract_id.id),\
                                                                                ('item','=',rec.item.id),
                                                                                ('stage_id','=',rec.stage_id.id),
                                                                                ('id','<',rec.id),
                                                                                ('parent_id.state','=','confirm')
                                                                                ])
                rec.previous_qty = sum(lines_pre_ids.mapped('qty'))



    @api.depends('qty','percentage','contract_line_id','other_prec')
    def get_price_cost(self):
        for rec in self:
            rec.amount=round(rec.other_prec/100,2)*(rec.contract_line_id.total_value)

            rec.prec_price=round((round(rec.percentage/100,2)*rec.amount),2)
            print(">>>>>>>>>>>>>>>>>>>",rec.contract_line_id.total_value,rec.other_prec)

    @api.depends('qty','contract_line_id')
    def get_percentage(self):
        for rec in self:
            rec.percentage=0
            if rec.contract_line_id.qty>0:
                rec.percentage=round((rec.qty/rec.contract_line_id.qty)*100,2)


    @api.onchange('qty')
    def _onchange_qty(self):
        if self.remind_qty > 0:
            self.remind_qty -= self.qty
            if self.remind_qty < 0:
                self.remind_qty = 0

    def unlink(self):
        for rec in self:
            if rec.parent_id.state != 'draft':
                raise ValidationError("You  Cann't delete ")
        res = super(Engineerlines, self).unlink()
        return res
