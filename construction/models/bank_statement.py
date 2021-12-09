from odoo import models, fields, api
from lxml import etree
class move(models.Model):
    _inherit = 'account.move'

    # @api.model
    # def create(self,vals):
    #     res=super(move, self).create(vals)
    #     print(">>>>>>>>>>>>>>>>>>>>>>>@@@@@22",res.statement_line_id)
    #     print(">>>>>>>>>>>>>>>>>>>>>>>@@@@@22",res.statement_line_id.product_id)
    #     print(">>>>>>>>>>>>>>>>>>>>>>>@@@@@22",res.statement_line_id.project_id)
    #     if res.statement_line_id:
    #         res.project_id=res.statement_line_id.project_id.id
    #         if res.statement_line_id.product_id:
    #             for rec in res.line_ids:
    #                 if res.statement_line_id.product_id:
    #                  rec.product_id = res.statement_line_id.product_id.id
    #                 if res.statement_line_id.item:
    #                         rec.item=res.statement_line_id.item
    #     return res



class BankStatment(models.Model):
    _inherit = 'account.bank.statement'
    project_id = fields.Many2one("project.project",string="Project")
    def button_post(self):
        res = super(BankStatment, self).button_post()
        for rec in self.line_ids:
            account_move_line = self.env['account.move.line'].search([('statement_line_id','=',rec.id)])

            for line in account_move_line:
                if rec.project_id:
                    line.move_id.project_id=rec.project_id.id
                if rec.product_id:
                     line.product_id = rec.product_id.id
                if rec.item:
                            line.item=rec.item.id
        return res
    def write(self, vals):
        res = super(BankStatment, self).write(vals)

        if 'project_id' in vals:
            for rec in self.line_ids:
                move_line = self.env['account.move.line'].search([('statement_line_id','=',rec.id)])
                for rec in move_line:
                    rec.move_id.project_id=vals.get('project_id')

        return res







class BankStatmentLine(models.Model):
    _inherit = 'account.bank.statement.line'
    project_id = fields.Many2one(related='statement_id.project_id',store=True,index=True)
    job_id = fields.Many2one("construction.job.cost",string="Job",domain="[('project_id','=',project_id)]")
    item_ids = fields.Many2many('product.item', "item_id", "line_ids", string='Item', compute='_get_item_list')
    item = fields.Many2one('product.item', string='Item', domain="[('id','in',item_ids)]")
    product_ids = fields.Many2many('product.product', "product_id", "line_ids", string='Product',
                                   compute='_get_product_list')
    product_id = fields.Many2one("product.product", string="Product", domain="[('id','in',product_ids)]")
    uom_id = fields.Many2one(related='product_id.uom_id',store=True,index=True)


    @api.depends('project_id', 'item')
    def _get_product_list(self):
        for rec in self:

            ids, domain = [], []
            rec.product_ids = []
            if rec.project_id:
                domain.append(('project_id', '=', rec.project_id.id))
            if rec.item:
                domain.append(('item', '=', rec.item.id))

            pro = self.env['construction.job.cost'].search(domain)
            for mat in pro.expense_ids:
                rec.product_ids = [(4, mat.product_id.id)]

            for mat in pro.labour_ids:
                rec.product_ids = [(4, mat.product_id.id)]
            for mat in pro.equipment_ids:
                rec.product_ids = [(4, mat.product_id.id)]
    @api.depends('project_id')
    def _get_item_list(self):
        ids = []
        for rec in self:
            rec.item_ids = []
            if rec.project_id:
                pro = self.env['project.project'].search([('id', '=', rec.project_id.id)])
                for ten in pro.tender_ids:
                    rec.item_ids = [(4, ten.item.id)]




    def write(self, vals):
        res = super(BankStatmentLine, self).write(vals)

        if 'item' in vals:

            move_line = self.env['account.move.line'].search([('statement_line_id','=',self.id)])
            for rec in move_line:
                rec.item=vals.get('item')
        if 'product_id' in vals:

            move_line = self.env['account.move.line'].search([('statement_line_id','=',self.id)])
            for rec in move_line:
                rec.product_id=vals.get('product_id')


        return res
