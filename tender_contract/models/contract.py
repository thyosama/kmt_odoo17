from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class contract(models.Model):
    _inherit = 'construction.contract'
    project_id = fields.Many2one("project.project", string="Project", domain="[('type','!=','draft')]")
    lines_id = fields.One2many("construction.contract.line", "contract_id", compute='_onchnage_project', store=True,
                               index=1, readonly=False)
    order_id = fields.Many2one("construction.sale.order", string="Referance Financial Offer")

    @api.depends("project_id")
    def _onchnage_project(self):

        if self.project_id:
            order_id = self.env['construction.sale.order'].search([('project_id', '=', self.project_id.id),
                                                                   ('state', '=', 'confirm')], limit=1)
            lines = []
            for rec in self.lines_id:
                rec.unlink()
            if order_id:
                self.order_id = order_id
                for rec in self.order_id.order_lines:

                    if rec.display_type==False:
                        lines.append((0, 0, {
                            'code': rec.name,
                            'item': rec.item.id,
                            'name': rec.description,
                            'qty': rec.qty,
                            'notes': rec.notes,
                            'price_unit': rec.price, 'discount': rec.discount,
                            'type': 'owner', 'tender_id': rec.tender_id.id,


                        }))
                    else:
                        print(">>>>>>>>>>>>>>>..")
                        lines.append((0, 0, {
                            'display_type':rec.display_type,

                            'name': rec.name
                        }))

                if self.type == 'owner':
                    self.lines_id = lines
            else:
                self.order_id = ''
                for rec in self.lines_id:
                    rec.unlink()


class ContractLine(models.Model):
    _inherit = 'construction.contract.line'
    tender_id = fields.Many2one('construction.tender', string="Tender ID")

    # @api.onchange('item')
    # def get_item_at_project(self):
    #     if self.contract_id.project_id:
    #         item = self.env['construction.tender'].search([('project_id', '=', self.contract_id.project_id.id)])
    #         ids = []
    #         for rec in item.item:
    #             ids.append(rec.id)
    #         domain = {'item': [('id', 'in', ids)]}
    #
    #         return {'domain': domain}

    @api.onchange('tender_id')
    def _get_tender_ids(self):

        if self.sup_contract_id.project_id:

            domain = {'tender_id': [
                ('id', 'in', self.sup_contract_id.project_id.tender_ids.ids)]
            }
            return {'domain': domain}
        elif self.contract_id.project_id:

            domain = {'tender_id': [('id', 'in', self.contract_id.project_id.tender_ids.ids)]
                      }

            return {'domain': domain}



    @api.model
    def create(self, vals):
        res = super(ContractLine, self).create(vals)
        for rec in self:
            if 'code' in vals:
                res.tender_id = self.env['construction.tender'].search([('code', '=', rec.code),
                                                                        ('project_id', '=',
                                                                         rec.contract_id.project_id.id)])
            # if res.contract_id.type == 'supconstractor':
            #     res.code = self.env['construction.tender'].search([('id', '=', rec.tender_id.id),
            #                                                        ('project_id', '=',
            #                                                         rec.contract_id.project_id.id)])

        return res


