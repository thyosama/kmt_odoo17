from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime


class WBS_Item(models.Model):
    _name = 'wbs.item'
    name = fields.Many2one('project.project', required=True, string="Project")
    partner_id = fields.Many2one(related="name.partner_id")
    item_ids = fields.One2many("wbs.item.line", "wbs_id", string="Lines")


class WBS_lines(models.Model):
    _name = "wbs.item.line"

    name = fields.Char("Name")
    wbs_id = fields.Many2one("wbs.item")
    project_id = fields.Many2one(related='wbs_id.name', string="Project")


class WBS_distribution(models.Model):
    _name = 'wbs.distribution'
    name = fields.Many2one('project.project', required=True, string="Project")
    partner_id = fields.Many2one(related="name.partner_id")
    item_ids = fields.One2many("wbs.distribution.line", "wbs_id", string="Lines", )

    _sql_constraints = [
        ('project_uniq', 'UNIQUE (name)', 'You can not have  the same project WBS !')
    ]
    def unlink(self):
        for rec in self.item_ids:
            rec.unlink()
        return  super(WBS_distribution, self).unlink()

    @api.constrains("item_ids")
    def _get_tender_qty(self):
        for record in self.item_ids:
            lines = self.env['wbs.distribution.line'].search([('tender_id', '=', record.tender_id.id)])
            qty = 0


            for rec in lines:

                qty += rec.qty_item

            if qty > record.tender_id.qty:
                raise ValidationError("You enter quantity greater then tender %s Quantity %s" % (
                    record.qty, record.tender_id.description))


class WBS_distribution_line(models.Model):
    _name = "wbs.distribution.line"
    wbs_id = fields.Many2one("wbs.distribution")
    tender_id = fields.Many2one("construction.tender", string="Tender Desc")
    qty = fields.Float(related='tender_id.qty', string="Tender Quantity")
    item_wbs = fields.Many2one("wbs.item.line", string="wbs-item")
    qty_item = fields.Float("distribution quantity")

    @api.onchange('item_wbs')
    def get_wbs_id(self):
        webs = self.env['wbs.item'].search([('name', '=', self.wbs_id.name.id)])
        ids = []

        if webs:
            for rec in webs.item_ids:
                ids.append(rec.id)
            domain = {'item_wbs': [('id', 'in', ids)]}

            return {'domain': domain}

    @api.onchange('tender_id')
    def change_domian(self):
        domain = {'tender_id': [('type', '=', 'transcation'),
                                ('project_id', '=', self.wbs_id.name.id)]}

        return {'domain': domain}


class WBS_Automatic(models.Model):
    _name = 'wbs.distribution.automatic'
    tender_id = fields.Many2many("construction.tender", "tender_auto", "id", string="Tender Desc")
    line_ids = fields.One2many("wbs.distribution.automatic.line", "wbs_id")
    name = fields.Many2one('project.project', required=True, string="Project")
    partner_id = fields.Many2one(related="name.partner_id")
    
    

        

    @api.constrains("line_ids")
    def _get_precentage(self):
        prec = 0
        for rec in self.line_ids:
            prec += rec.precentage
        if prec > 100:
            raise ValidationError("Please Check you precentage")

    @api.onchange('tender_id','name')
    def change_domian(self):



        ids =[]
        tender_id = self.env['construction.tender'].search([('project_id','=',self.name.id)])
        for rec in tender_id:
            web_id = self.env['wbs.distribution.line'].search([('wbs_id.name','=',self.name.id),('tender_id','=',rec.id)],limit=1)

            if not web_id:
                ids.append(rec.id)

        domain = {'tender_id': [ ('id', 'in', ids)]}
        return   {'domain': domain}

        domain = {'tender_id': [('type', '=', 'transcation'),
                                ('project_id', '=', self.name.id)]}
    def _get_child_tender(self,id,list,tender_ids):
        web_id = self.env['wbs.distribution'].search([('name', '=', self.name.id)])
        tender_id = self.env['construction.tender'].search([('parent_item', '=', id)])

        for rec in tender_id:

            for record in self.line_ids:
                if web_id:
                    line_dis = self.env['wbs.distribution.line']. \
                        search([('wbs_id', '=', web_id.id), ('tender_id', '=', rec.id)])
                    if line_dis:
                        line_dis.unlink()
                if rec.id not in tender_ids:
                    tender_ids.append(rec.id)
                list.append((0, 0, {

                    'tender_id': rec.id,
                    'item_wbs': record.item_wbs.id,
                    'qty_item': rec.qty * (record.precentage / 100)
                }))
        return list,tender_ids

    def compute_wbs(self):

        web_id = self.env['wbs.distribution'].search([('name', '=', self.name.id)])
        list,tender_ids = [],[]

        for rec in self.tender_id:
            if rec.type=='main':
                list,tender_ids = self._get_child_tender(rec.id,list,tender_ids)

            else:

                for record in self.line_ids:
                    if web_id:
                        line_dis = self.env['wbs.distribution.line']. \
                            search([('wbs_id', '=', web_id.id),('tender_id', '=', rec.id)])
                        if line_dis:
                            line_dis.unlink()
                    if rec.id not in tender_ids:
                        list.append((0, 0, {

                            'tender_id': rec.id,
                            'item_wbs': record.item_wbs.id,
                            'qty_item': rec.qty * (record.precentage / 100)
                        }))

        if web_id:
            web_id.write({
                'item_ids': list
            })
        else:
            self.env['wbs.distribution'].create({
                'name': self.name.id,
                'item_ids': list

            })


class WBS_Automaticline(models.Model):
    _name = 'wbs.distribution.automatic.line'
    item_wbs = fields.Many2one("wbs.item.line", string="wbs-item",required=1)
    precentage = fields.Float("Precentage %")
    wbs_id = fields.Many2one("wbs.distribution.automatic")


    @api.onchange('item_wbs')
    def get_wbs_id(self):
        webs= self.env['wbs.item'].search([('name','=',self.wbs_id.name.id)])
        ids=[]

        if webs:
            for rec in webs.item_ids:
                ids.append(rec.id)
            domain = {'item_wbs': [('id','in',ids)]}

            return {'domain': domain}
