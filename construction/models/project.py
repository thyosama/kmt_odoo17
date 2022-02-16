from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    # parent_id = fields.Many2one("project.project", string="Parent")
    # child_ids = fields.One2many(comodel_name='project.project', inverse_name='parent_id', string='Children')
    partner_id = fields.Many2one("res.partner", string="Customer")
    created_date = fields.Date("Created Date", default=datetime.today())
    consultant = fields.Many2one("res.partner", string="Consultant")
    tender_ids = fields.One2many("construction.tender", "project_id", string="Tenders")
    job_cost_count = fields.Integer()
    manager_id = fields.Many2one("res.partner", string="Manager")
    is_quotation = fields.Boolean()

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

    def create_job_ct(self):

        job_cost_count = 0

        for rec in self.tender_ids:
            if rec.type == 'transcation':

                job_id = self.env['construction.job.cost'].search([('tender_id', '=', rec.id)])

                if job_id:
                    rec.state = 'job_cost'
                    job_cost_count += 1
                    job_id.update({
                        # 'name': 'Job Cost/' + rec.code,
                        'project_id': rec.project_id.id,
                        'partner_id': self.partner_id.id if self.partner_id else '',
                        'code': rec.code,
                        'type': rec.type,
                        'item': rec.item.id,
                        'description': rec.description,
                        'uom_id': rec.uom_id.id,
                        'qty': rec.qty,
                        'status': rec.status,
                        'notes': rec.notes,
                        'tender_id': rec.id, }
                    )

                else:

                    job_cost_count += 1
                    rec.state = 'job_cost'
                    self.env['construction.job.cost'].create({
                        # 'name': 'Job Cost/' + rec.code,
                        'project_id': rec.project_id.id,
                        'partner_id': self.partner_id.id if self.partner_id else '',
                        'code': rec.code,
                        'type': rec.type,
                        'item': rec.item.id,
                        'description': rec.description,
                        'uom_id': rec.uom_id.id,
                        'qty': rec.qty,
                        'status': rec.status,
                        'notes': rec.notes,
                        'tender_id': rec.id, }
                    )

        self.job_cost_count = job_cost_count

    def view_job_cost(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Break Down ',
            'view_mode': 'tree,form',
            'res_model': 'construction.job.cost',
            'domain': [('project_id', '=', self.id)],
            'target': 'current',

        }

    def view_quotation(self):
        view = self.env.ref('construction.construction_sale_order_tree')
        view_form = self.env.ref('construction.construction_sale_order_form')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Financial Offer',
            'view_mode': 'tree,form',
            'res_model': 'construction.sale.order',
            'domain': [('project_id', '=', self.id)],
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            'target': 'current',

        }

    def create_quotation(self):
        sales_order = self.env['construction.sale.order'].search([('project_id', '=', self.id)])
        self.is_quotation = True
        job_cost_ids = self.env['construction.job.cost'].search(
            [('project_id', '=', self.id), ('state', '=', 'quotation')])

        lines = []
        for rec in self.tender_ids:
            job_cost_ids = self.env['construction.job.cost'].search(
                [('project_id', '=', self.id), ('tender_id', '=', rec.id), ('state', '=', 'quotation')])
            if rec.type == 'main' or job_cost_ids:
                lines.append((0, 0, {
                    'code': rec.code,
                    'description': rec.description,
                    'item': rec.item.id,
                    'qty': rec.qty,
                    'uom_id': rec.uom_id.id,
                    'price_unit': rec.price_unit,
                    'type': rec.type,
                    'tender_id': rec.id,

                }))
        if sales_order:
            for rec in sales_order.order_lines:
                rec.unlink()
            sales_order.write({
                'partner_id': self.partner_id.id,
                'project_id': self.id,
                'order_lines': lines, 'created_date': self.created_date,
            })
        else:
            sales = self.env['construction.sale.order'].create({
                'partner_id': self.partner_id.id,
                'project_id': self.id,
                'order_lines': lines, 'created_date': self.created_date,
            })
            sales.name = "QUT/" + str(sales.id).zfill(6)
