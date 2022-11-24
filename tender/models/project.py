from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    partner_id = fields.Many2one("res.partner", string="Customer")
    created_date = fields.Date("Created Date", default=datetime.today(), tracking=True)
    consultant = fields.Many2one("res.partner", string="Consultant", tracking=True)
    tender_ids = fields.One2many("construction.tender", "project_id", string="Tenders")
    job_cost_count = fields.Integer(copy=False, compute='get_job_cost_ids_2')
    quotation_count = fields.Integer(copy=False, compute='get_quotation_count')
    manager_id = fields.Many2one("res.partner", string="Manager", tracking=True)
    is_quotation = fields.Boolean(tracking=True)
    type = fields.Selection([('draft', 'Draft'), ('project', 'Project')], default="project", tracking=True)
    project_number = fields.Char(compute='get_project_number', tracking=True)
    date_from = fields.Date("Project Begining", tracking=True)
    date_to = fields.Date("Project End Date", tracking=True)
    dif = fields.Char("Differance", compute='get_differance')
    date_contract = fields.Date("Contract Date", tracking=True)
    tender_submission_date = fields.Date(tracking=True)
    location_acquisition_date = fields.Date(tracking=True)
    analytic_account = fields.Many2one("account.analytic.account")
    project_reference = fields.Char(tracking=True)
    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())
    currancy_ids = fields.One2many("project.currency", "project_id")

    total_value = fields.Float(compute='get_total_value_tender_lines')
    indirect_id = fields.Many2one("indirect.cost",copy=False)
    top_sheet_id = fields.Many2one("top.sheet",copy=False)


    @api.constrains("tender_ids")
    def get_top_sheet_indirect(self):
        cost=top_sheet=0
        for rec in self.tender_ids:

            cost+=rec.indirect_cost
            top_sheet+=rec.profit


        if self.indirect_id and self.indirect_id.total!=cost:
            raise ValidationError("Indirect must be equal")
        if self.top_sheet_id and self.top_sheet_id.total_value!=top_sheet:
            raise ValidationError("Top Sheet must be equal")
    @api.depends('tender_ids','tender_ids.total_value')
    def get_total_value_tender_lines(self):
        for rec in self:
            total_value=0
            for line in rec.tender_ids:
                total_value+=line.total_value
            rec.total_value=total_value

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    def update_ratio_currancy(self):
        job_ids = self.env['construction.job.cost'].search([('techical_type','=',False),('state','!=','quotation'),('project_id', '=', self.id)])

        for record in job_ids:
            for rec in record.material_ids:
                currancy_id = self.env['project.currency'] \
                    .search([('currancy_id', '=', rec.currancy_id.id), ('project_id', '=', self.id)])

                if currancy_id:
                    rec.ratio = currancy_id.ratio
                if record.state != 'quotation':
                    rec._compute_sub_total()
                    record._compute_all_values()
                    record.compute_total_with_qty()
            if record.tender_id and record.state in( 'quotation','approve'):
                record.tender_id.price_unit = record.total_value_all
                # record.tender_id.calculate_sales_price()
                # record.tender_id._get_total_value()

                    # record.action_approve()


    @api.depends('date_to', 'date_from')
    def get_differance(self):
        for rec in self:
            rec.dif = ''
            if rec.date_from and rec.date_to:
                rec.dif = rec.date_to - rec.date_from

    @api.depends('name')
    def get_project_number(self):
        for rec in self:
            rec.project_number = ''
            if rec.id:
                rec.project_number = "PR/" + str(rec.id).zfill(5)

    # @api.constrains('tender_ids')
    # def constrains_code(self):
    #     for rec in self.tender_ids:
    #
    #             lines = self.env['construction.tender'].search([
    #                 ('project_id', '=', self.id),
    #                 ('code', '=', rec.code),
    #                 ('id', '!=', rec.id),
    #             ], limit=1)
    #             print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", lines)
    #             if lines and rec.code:
    #                 raise ValidationError(_("Code [ %s ] Already Exist") % (self.code))



             

    def get_job_cost_ids_2(self):
        for rec in self:
            rec.job_cost_count = 0
            if rec.id:
                job_cost_ids = self.env['construction.job.cost'].sudo() \
                    .search([('techical_type','=',False),('active', 'in', (False, True)), ('project_id', '=', rec.id)], limit=1, order='id desc')
                rec.job_cost_count = job_cost_ids.version_num

    def get_quotation_count(self):
        for rec in self:
            rec.quotation_count = 0
            if rec.id:
                quotation_count_ids = self.env['construction.sale.order'].sudo().search(
                    [('active', 'in', (False, True)), ('project_id', '=', rec.id)])
                rec.quotation_count = len(quotation_count_ids)

    def create_job_ct(self):

        job_cost_count = 0
        self.clear_caches()
        job_cost_ids = self.env['construction.job.cost'].sudo().search([('techical_type','=',False),('project_id', '=', self.id)])
        job_cost_ids_2 = self.env['construction.job.cost'].sudo().search(
            [('techical_type','=',False),('active', '=', False), ('project_id', '=', self.id)])

        version_num = 1
        if job_cost_ids:
            for rec in job_cost_ids:
                new_job_id = rec.sudo().copy()

                new_job_id.state = 'draft'
                new_job_id.qty = new_job_id.tender_id.qty
                new_job_id.currancy_id = self.currancy_id.id
                new_job_id.version_num = rec.version_num + 1
                version_num = rec.version_num + 1
                new_job_id.version = "V/" + str(rec.version_num + 1).zfill(5)

                rec.active = False

                self.duplicte_job_cost(new_job_id, rec)
                new_job_id._compute_all_values()

            # self.job_cost_count = len(job_cost_ids)+len(job_cost_ids_2)
            if len(job_cost_ids) != len(self.tender_ids):
                for tend in self.tender_ids:
                    job_cost_id = self.env['construction.job.cost'].sudo().search(
                        [('techical_type','=',False),('tender_id', '=', tend.id), ('project_id', '=', self.id)])

                    if not job_cost_id and not tend.display_type:
                        # self.job_cost_count+=1
                        tend.state = 'job_cost'
                        self.env['construction.job.cost'].sudo().create({
                            # 'name': 'Job Cost/' + rec.code,
                            'project_id': tend.project_id.id,
                            'partner_id': self.partner_id.id if self.partner_id else '',
                            'code': tend.code,
                            'item': tend.item.id,
                            'description': tend.name,
                            'uom_id': tend.uom_id.id,
                            'qty': tend.qty,

                            'notes': tend.notes,
                            'tender_id': tend.id,
                            'related_job': tend.related_job.id,
                            'currancy_id': self.currancy_id.id,
                            'version_num': version_num,
                            'version': "V/" + str(version_num).zfill(5),
                        }
                        )


        else:
            for rec in self.tender_ids:

                job_id = self.env['construction.job.cost'].sudo().search([('techical_type','=',False),('tender_id', '=', rec.id)])

                if rec.display_type == False:
                    job_cost_count += 1
                    rec.state = 'job_cost'
                    self.env['construction.job.cost'].sudo().create({
                        # 'name': 'Job Cost/' + rec.code,
                        'project_id': rec.project_id.id,
                        'partner_id': self.partner_id.id if self.partner_id else '',
                        'code': rec.code,
                        'item': rec.item.id,
                        'description': rec.name,
                        'uom_id': rec.uom_id.id,
                        'qty': rec.qty,

                        'notes': rec.notes,
                        'tender_id': rec.id,
                        'related_job': rec.related_job.id,
                        'version_num': 1,
                        'version': "V/" + str(1).zfill(5),
                    }
                    )

            # self.job_cost_count = job_cost_count

    def view_job_cost(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimation ',
            'view_mode': 'tree,form',
            'res_model': 'construction.job.cost',
            'domain': [('techical_type','=',False),('active', 'in', (False, True)), ('project_id', '=', self.id)],
            'context': {"search_default_version": 1},
            'target': 'current',

        }

    def view_quotation(self):
        view = self.env.ref('tender.construction_sale_order_tree')
        view_form = self.env.ref('tender.construction_sale_order_form')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Financial Offer',
            'view_mode': 'tree,form',
            'res_model': 'construction.sale.order',
            'domain': [('active', 'in', (False, True)), ('project_id', '=', self.id)],
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            # 'context': {"search_default_version": 1},
            'target': 'current',

        }

    def create_quotation(self):
        sales_order = self.env['construction.sale.order'].sudo().search([('project_id', '=', self.id)], order='id asc')
        sales_order_all_ids = self.env['construction.sale.order'].sudo().search(
            [('active', 'in', (False, True)), ('project_id', '=', self.id)], order='id asc')
        self.is_quotation = True
        job_cost_ids = self.env['construction.job.cost'].sudo().search(
            [('techical_type','=',False),('project_id', '=', self.id), ('state', '=', 'quotation')])

        lines = []
        version_num=estimation_version = 1

        for rec in self.tender_ids:
            job_cost_ids = self.env['construction.job.cost'].sudo().search(
                [('techical_type','=',False),('project_id', '=', self.id), ('tender_id', '=', rec.id), ('state', '=', 'quotation')])
            if job_cost_ids:
                estimation_version=job_cost_ids.version_num
                if rec.display_type==False:
                    lines.append((0, 0, {
                        'name': rec.code,
                        'description': rec.name,
                        'item': rec.item.id,
                        'qty': rec.qty,
                        'uom_id': rec.uom_id.id,
                        'price_unit': rec.sale_price,
                        'total_value':rec.total_value,

                        'tender_id': rec.id,
                        'display_type':rec.display_type

                    }))
            if rec.display_type!=False:
                lines.append((0, 0, {
                    'name': rec.name,
                    'display_type': rec.display_type


                }))

        name_so = ''
        if sales_order:
            version_num = len(sales_order_all_ids) + 1

            for rec in sales_order:
                name_so = rec.name

                rec.active = False

            # sales_order.write({
            #     'partner_id': self.partner_id.id,
            #     'project_id': self.id,
            #     'order_lines': lines, 'created_date': self.created_date,
            # })

        if lines:
            sales = self.env['construction.sale.order'].sudo().create({
                'partner_id': self.partner_id.id,
                'project_id': self.id,
                'order_lines': lines, 'created_date': self.created_date,
                'version_num': version_num,
                'version': "V/" + str(version_num).zfill(5),
                'estimation_version': "V/" + str(estimation_version).zfill(5),
            })
            if name_so:
                sales.name = name_so
            else:

                sales.name = "QUT/" + str(sales.id).zfill(6)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(Project, self).copy()
        res.type = self.type
        for rec in self.tender_ids:
            self.env['construction.tender'].create({
                'code': rec.code,
                'item': rec.item.id,
                'name': rec.name,
                'qty': rec.qty,
                'display_type': rec.display_type,
                'tax_id': rec.tax_id,
                'price_unit': rec.price_unit,
                'project_id': res.id
            })
        return res

    def confirm_as_project(self):
        self.type = 'project'

    def upload_tender(self):
        view = self.env.ref('tender.mutli_edit_tender_view_tree')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Tender ',
            'view_mode': 'tree',
            'view_id': view.id,
            'res_model': 'construction.tender',
            'domain': [('state', '=', 'main'), ('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
            'target': 'current',


        }
