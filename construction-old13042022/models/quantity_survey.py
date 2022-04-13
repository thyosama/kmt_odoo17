from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class QuantitySurvey(models.Model):
    _name = 'quantity.survey'

    name = fields.Char("sequence",compute='get_name')

    project_id = fields.Many2one(comodel_name='project.project', string='Project Name ', )
    partner_id = fields.Many2one(comodel_name='res.partner', related="project_id.partner_id",string='Customer')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)

    quantity_survey_lines = fields.One2many(comodel_name='quantity.survey.line', inverse_name='quantity_survey_id',
                                            string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('cancel','Cancel')], string="State", default='draft')
    estimate_cost_value = fields.Float(compute='get_cost_sale_value',store=True,index=True)
    estimate_sales_value = fields.Float(compute='get_cost_sale_value',store=True,index=True)
    @api.depends('quantity_survey_lines')
    def get_cost_sale_value(self):
        for record in self:
            for rec in record.quantity_survey_lines:
                record.estimate_cost_value+=rec.cost_value
                record.estimate_sales_value+=rec.sale_value
    @api.depends('project_id')
    def get_name(self):
        for rec in self:
            rec.name='QS'+"-"+ str(rec.id).zfill(5)
    def action_confrim(self):
        self.state='confirm'

    def action_cancel(self):
        servey_ids = self.env['quantity.survey'].search([('project_id','=',self.project_id.id)],order=' id desc',limit=1)
        if servey_ids.id>self.id and servey_ids.state!='cancel':
            raise ValidationError("Cann't cancel ")
        else:
            self.state='cancel'
    def action_set_draft(self):
        servey_ids = self.env['quantity.survey'].search([('project_id','=',self.project_id.id)],order=' id desc',limit=1)

        if servey_ids.id>self.id and servey_ids.state!='cancel':
            raise ValidationError("Cann't set draft ")
        else:
            self.state='draft'
    @api.onchange('project_id')
    def project_id_changed(self):
        lines = []
        if self.project_id:
            self.partner_id = self.project_id.partner_id.id
            # qs = self.env['quantity.survey'].search([('project_id','=',self.project_id.id)],order='id desc')
            # for rec in qs.quantity_survey_lines:
            #     lines.append((0,0,{
            #
            #
            #     }))


    @api.model
    def create(self,vals):
        res =super(QuantitySurvey, self).create(vals)

        last_qs_id = self.env['quantity.survey'].search([
            ('project_id', '=', res.project_id.id),
            ('partner_id', '=', res.partner_id.id),
            ('id', '!=', res.id),
        ], limit=1, order='id desc')

        if last_qs_id:
            for line in last_qs_id.quantity_survey_lines:
                new_line = self.env['quantity.survey.line'].create({
                    'quantity_survey_id': res.id,
                    'tender_line': line.tender_line.id,
                    'item': line.item.id,
                    'code': line.code,
                    'type': line.type,
                    'tender_qty': line.tender_qty,

                    'cost_price': line.cost_price,
                    'sale_price': line.sale_price,
                    'job_id': line.job_id.id,
                    'uom_id': line.uom_id.id,
                    'notes': line.notes,
                    'duration': line.duration,
                })

                new_line.get_variance()
                new_line._get_dif()
                new_line.get_tender_job_id()
                new_line._onchange_current_qty()
                new_line.compute_quantities_cost()
        return res

    def unlink(self):
        for rec in self.quantity_survey_lines:
            rec.unlink()
        res = super(QuantitySurvey, self).unlink()

        return res
    #         if self.project_id.tender_ids:
    #             self.quantity_survey_lines = None
    #             for rec in self.project_id.tender_ids:
    #                 lines.append((0, 0, {
    #                     'code': rec.code,
    #                     'item': rec.item.id,
    #                     'sale_price': rec.item.id,
    #                     'cost_price': rec.item.id,
    #                     'description': rec.description,
    #                     'type': rec.type,
    #                     'tender_qty': rec.qty,
    #
    #                 }))
    #             self.quantity_survey_lines = lines

    @api.constrains('quantity_survey_lines')
    def _check_code(self):
        for rec in self.quantity_survey_lines:
            if rec.code and rec.quantity_survey_id.project_id:
                tender_ids = self.env['construction.tender'].search(
                    [('code', '=', rec.code), ('project_id', '=', rec.quantity_survey_id.project_id.id)])
                if not tender_ids:
                    raise ValidationError("You select Code not found at Tender %s" % (rec.code))


class QuantitySurveyLine(models.Model):
    _name = 'quantity.survey.line'

    _rec_name = 'code'
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], related='quantity_survey_id.state',string="State",
                             default='draft')
    quantity_survey_id = fields.Many2one(comodel_name='quantity.survey', )
    project_id = fields.Many2one(related='quantity_survey_id.project_id',store=True,index=True)

    tender_line = fields.Many2one('construction.tender', string='Tender item', required=1,domain="[('project_id','=',project_id)]")
    # item = fields.Many2one('product.item', string='Item', required=1)
    item = fields.Many2one(related='tender_line.item')
    code = fields.Char(related='tender_line.code',string="Code")
    description = fields.Char("Desc")
    type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')],related='tender_line.type', string='Type')
    uom_id = fields.Many2one(related='item.uom_id', string="UOM")
    tender_qty = fields.Float("Tender Quantity",related='tender_line.qty',store=True,index=True)
    last_qty = fields.Float("Previous Quantity",compute='get_last_qty')
    current_qty = fields.Float("Current Quantity")
    total_qty = fields.Float("Total Quantity")
    remaining_qty = fields.Float("Remaining Quantity", compute="compute_quantities_cost", store=True)
    cost_price = fields.Float("Cost Price")
    cost_value = fields.Float("Cost Value", compute="compute_quantities_cost", store=True)
    sale_price = fields.Float("Sale Price")
    sale_value = fields.Float("Sale Value", compute="compute_quantities_cost", store=True)
    duration = fields.Integer(string='duration/day', )
    notes = fields.Char(string='Notes')
    project_id = fields.Many2one(comodel_name="project.project", related='quantity_survey_id.project_id',
                                 string="Project",
                                 store=True, index=True)  # related="quantity_survey_id.project_id",
    job_id = fields.Many2one("construction.job.cost", readonly=True, compute='get_tender_job_id')
    tender_id = fields.Many2one('construction.tender', compute='get_tender_job_id', store=True, index=True)
    start_date = fields.Date(related='job_id.start_date', store=True, index=True)
    end_date = fields.Date(related='job_id.end_date', store=True, index=True)
    dif = fields.Integer("Differance Date", compute='_get_dif')
    time_variance = fields.Float("Time variance", compute='get_variance')
    @api.depends('tender_line')
    def get_last_qty(self):
        for rec in self:
            last_qs_id = self.env['quantity.survey.line'].search([
                ('project_id', '=', rec.project_id.id),
                ('tender_line','=',rec.tender_line.id),
                ('quantity_survey_id', '<', rec._origin.quantity_survey_id.id),('state','!=','cancel')
            ], limit=1, order='id desc')
            rec.last_qty=0
            if last_qs_id:
                rec.last_qty = last_qs_id.total_qty


    @api.depends('dif', 'duration')
    def get_variance(self):
        for rec in self:
            rec.time_variance = int(rec.dif) - rec.duration

    @api.depends('start_date', 'end_date')
    def _get_dif(self):
        self.dif = ''
        for rec in self:
            dif = ''
            if rec.start_date and rec.end_date:
                rec.dif = (rec.end_date - rec.start_date).days

    @api.depends('tender_line')
    def get_tender_job_id(self):
        for rec in self:
            rec.job_id = False
            rec.tender_id = False
            tender_ids = self.env['construction.tender'].search(
                [('code', '=', rec.tender_line.code),('project_id','=',rec.quantity_survey_id.project_id.id) ], limit=1)
            if tender_ids:
                rec.tender_id = tender_ids.id
            job_ids = self.env['construction.job.cost'].search(
                [('code', '=', rec.tender_line.code),('project_id','=',rec.quantity_survey_id.project_id.id)], limit=1)
            if job_ids:
                rec.job_id = job_ids.id



    @api.onchange('current_qty','last_qty')
    def _onchange_current_qty(self):
        self.total_qty = self.current_qty

    @api.depends('total_qty', 'tender_qty', 'last_qty')
    def compute_quantities_cost(self):
        for rec in self:
            if rec.tender_qty:
                rec.total_qty+=rec.last_qty
                rec.remaining_qty = rec.tender_qty - rec.total_qty
            if rec.total_qty and rec.cost_price:
                rec.cost_value = rec.total_qty * rec.cost_price
            if rec.total_qty and rec.sale_price:
                rec.sale_value = rec.total_qty * rec.sale_price

    @api.onchange('tender_line', 'item', 'project_id')
    def _onchange_item(self):
        for rec in self:
            if not rec.project_id:
                raise ValidationError('You Must select Project')
            rec.cost_price = 0
            job_cost_id=''
            if rec.tender_line:
                job_cost_id = self.env['construction.job.cost'].search([
                    ('code', '=', rec.tender_line.code),
                    ('project_id', '=', rec.quantity_survey_id.project_id.id),
                ], limit=1)
            if job_cost_id:
                rec.cost_price = job_cost_id.total_value_all

            rec.sale_price = rec.tender_line.price_unit
            rec.description=rec.tender_line.description
            rec.type = rec.tender_line.type
            rec.tender_qty = rec.tender_line.qty
            # contract_id = self.env['construction.contract'].search([('project_id', '=', rec.project_id.id)], limit=1)
            # for line in contract_id.lines_id:
            #     if line.item == rec.item:
            #         rec.sale_price = line.price_unit
            last_qs_id = self.env['quantity.survey']

            if self.tender_line:
                last_qs_id = self.env['quantity.survey'].search([
                    ('project_id', '=', rec.project_id.id),
                    ('partner_id', '=', rec.quantity_survey_id.partner_id.id),
                    ('id', '!=', self._origin.quantity_survey_id.id),
                ], limit=1, order='id desc')



        res = {}
        tender_line = []
        self.type = self.tender_line.type
        self.tender_qty = self.tender_line.qty


    # @api.model
    # def create(self,vals):
    #     res = super(QuantitySurveyLine, self).create(vals)
    #     job_ids = self.env['construction.job.cost'].search(
    #         [('code', '=', res.code), ('project_id', '=', res.project_id.id)],limit=1)
    #     if job_ids:
    #         res.job_id=job_ids.id
    #     return res
