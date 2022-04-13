from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit= 'account.move.line'

    @api.model
    def _search_parent_id(self, operator, value):
        if operator == 'like':
            operator = 'ilike'
        return [('name', operator, value)]

    parent_project_id = fields.Many2one("parent.project", string="Parent", compute='compute_parent_id', store=True,
                                search=_search_parent_id,)

    @api.depends('project_id')
    def compute_parent_id(self):
        for rec in self:
            rec.parent_project_id = rec.project_id.parent_project_id.id


class AccountInvoiceLine(models.Model):
    _inherit= 'account.invoice.line'

    remaining = fields.Float("remaining",compute='get_remaining_qty',store=True)
    actual_qty = fields.Float("Actual Qty",compute='get_actual_qty',store=True)

    @api.depends('contract_qty','quantity')
    def get_remaining_qty(self):
        for rec in self:
            rec.remaining=rec.contract_qty-rec.quantity

    @api.depends('project_id', 'tender_id','date')
    def get_actual_qty(self):
        for rec in self:
            rec.actual_qty=0
            qs_lines =self.env['quantity.survey.line'].search(
                [('state', '=', 'confirm'), ('tender_line', '=', rec.tender_id.id)
                    , ('project_id', '=', rec.project_id.id),('date','<=',rec.date)],order='id desc',limit=1)
            if qs_lines:
                rec.actual_qty=sum(qs_lines.mapped('total_qty'))
