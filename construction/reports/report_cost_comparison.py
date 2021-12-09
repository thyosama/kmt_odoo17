from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import itertools
import pytz
_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.construction.report_cost_comparison"

    @api.model
    def _get_report_values(self, docids, data=None):
        project_id = data["form"]["project_ids"]


        qlines = self.env['quantity.survey.line'].search([('project_id','=',project_id)])
        lines,docs_line=[],[]
        for rec in qlines:

            docs_line.append(
                {
                    'item':rec.item,
                    'item_id':rec.item.id,
                    'uom_id':rec.uom_id,
                    'tender_qty':rec.tender_qty,
                    'duration':rec.duration,
                    'total_qty':rec.current_qty,
                    'project_id':project_id,

                }
            )

        docs = sorted(docs_line, key=lambda i: (i['item_id']))

        lst = []
        i = 0
        for key, group in itertools.groupby(docs, key=lambda x: (x['item'])):

            line = []

            tender_qty,duration,total_qty=0,0,0



            for item in group:
                tender_qty+=item['tender_qty']
                duration+=item['duration']
                total_qty+=item['total_qty']
            #job_ids = self.env['']


            lst.append(
                {
                    'item': key,
                    'item_id': key.id,
                    'uom_id': key.uom_id,
                    'tender_qty': tender_qty,
                    'duration': duration,
                    'total_qty':total_qty,
                    'remaing_qty':tender_qty-total_qty,
                    'prec':round((total_qty/tender_qty),2)*100 if tender_qty>0 else 0,
                    'type':'',
                    'job_cost_item':'',
                    'estimated_cost':'',
                    'estimated_qty':'',
                    'estimated_price':'',
                }
            )


        # product_ids = self._get_product_move_item(project_id, key)
        # for pro in product_ids:
        #     estimated_qty, estimated_cost = self._get_etimate_cost_price(pro, key, project_id)

        lines,pro_list=[],[]
        for record in lst:
            lines.append(
                {
                    'item': record['item'],
                    'item_id': record['item_id'],
                    'uom_id': record['uom_id'],
                    'tender_qty': record['tender_qty'],
                    'duration': record['duration'],
                    'total_qty': record['total_qty'],
                    'remaing_qty': record['remaing_qty'],
                    'prec': record['prec'],
                    'type': '',
                    'type_line':'main'

                }
            )
            lines,pro_list =self._get_marital_of_item(record['item_id'],project_id,lines)
            lines = self._get_product_move_item(project_id, record['item_id'],pro_list,lines)
            lines = self._get_labour_of_item(record['item_id'], project_id,lines)
            lines = self._get_expenses_of_item(record['item_id'], project_id,lines)
            lines = self._get_subconstractor_of_item(record['item_id'], project_id,lines)
            lines = self._get_equipment_of_item(record['item_id'], project_id,lines)

        return {
            # 'doc_ids': docs.ids,
            'doc_model': 'cost.comparison',

            'docs': lines,
            'lines': lines,
            'proforma': True
        }
    def _get_actual_cost_actual_qty(self,item,project_id,product_id):
        stock_move=self.env['stock.move'].search([('item','=',item),('project_id','=',project_id),
                                                  ('product_id','=',product_id)])
        move_line_ids = self.env['account.move.line'].search([('item', '=', item), ('project_id', '=', project_id),
                                                    ('product_id', '=', product_id)])
        actual_qty,actual_cost=0,0
        for rec in stock_move:
            if rec.picking_id.picking_type_id.code=='outgoing':
                actual_qty+=rec.product_uom_qty
        for rec in move_line_ids:
            if rec.move_id.move_type!='in_invoice' :
                if rec.type_invoice !='owner':
                    if not rec.move_id.stock_move_id:
                        actual_qty+=rec.quantity
                    actual_cost+=rec.credit
        return actual_qty,actual_cost





    def _get_marital_of_item(self,item,project_id,lines):
        marterial_id = self.env['construction.material'].search([('item','=',item),('job_id.project_id','=',project_id)])
        estimated_qty, estimated_cost=0,0
        lst,product_ids=[],[]
        result,product_ids = [],[]
        for rec in marterial_id:
            if rec.product_id.id not in product_ids:
                result.append(rec)
                product_ids.append(rec.product_id.id)
        product_ids=[]
        for rec in result:
            qs_line = self.env['quantity.survey.line'].search([('item','=',item),('project_id','=',project_id)])
            estimated_qty, estimated_cost = 0, 0
            for qs in qs_line:
                estimated_qty+=qs.current_qty*rec.planned_qty
                estimated_cost+=(qs.current_qty*rec.planned_qty)*rec.cost_unit
            actual_qty,actual_cost = self._get_actual_cost_actual_qty(item,project_id,rec.id)
            estimated_price=estimated_cost / estimated_qty if estimated_qty > 0 else 0
            actual_price=actual_cost / actual_qty if actual_qty > 0 else 0
            lines.append({
                 'item_id':item,
                'project_id':project_id,
                'job_cost_item': rec.product_id.name,
                'product_id': rec.product_id,
                'estimated_cost': estimated_cost,
                'estimated_qty': estimated_qty,
                'estimated_price':estimated_price ,
                'type_line': 'line',
                'actual_qty':actual_qty,
                'actual_price':actual_price,
                'actual_cost':actual_cost,
                'diffrence_qty':estimated_qty-actual_qty,
                'diffrence_price':estimated_price-actual_price,
                'diffrence_value':estimated_cost-actual_cost,
            })
            product_ids.append(rec.product_id.id)
        return lines,product_ids
    def _get_labour_of_item(self,item,project_id,lines):
        marterial_id = self.env['construction.labour'].search([('item','=',item),('job_id.project_id','=',project_id)])
        estimated_qty, estimated_cost=0,0
        lst,product_ids=[],[]
        result, product_ids = [], []
        for rec in marterial_id:
            if rec.product_id.id not in product_ids:
                result.append(rec)
                product_ids.append(rec.product_id.id)
        product_ids = []

        for rec in result:
            qs_line = self.env['quantity.survey.line'].search([('item','=',item),('project_id','=',project_id)])
            estimated_qty, estimated_cost = 0, 0
            for qs in qs_line:
                estimated_qty+=qs.current_qty*rec.planned_qty
                estimated_cost+=(qs.current_qty*rec.planned_qty)*rec.cost_unit
            actual_qty, actual_cost = self._get_actual_cost_actual_qty(item, project_id, rec.id)
            estimated_price = estimated_cost / estimated_qty if estimated_qty > 0 else 0
            actual_price = actual_cost / actual_qty if actual_qty > 0 else 0
            lines.append({
                'item_id': item,
                'project_id': project_id,
                'job_cost_item': rec.product_id.name,
                'product_id': rec.product_id,
                'estimated_cost': estimated_cost,
                'estimated_qty': estimated_qty,
                'estimated_price': estimated_price,
                'type_line': 'line',
                'actual_qty': actual_qty,
                'actual_price': actual_price,
                'actual_cost': actual_cost,
                'diffrence_qty': estimated_qty - actual_qty,
                'diffrence_price': estimated_price - actual_price,
                'diffrence_value': estimated_cost - actual_cost,
            })


        return lines
    def _get_expenses_of_item(self,item,project_id,lines):
        marterial_id = self.env['construction.expense'].search([('item','=',item),('job_id.project_id','=',project_id)])
        estimated_qty, estimated_cost=0,0
        lst,product_ids=[],[]
        result, product_ids = [], []
        for rec in marterial_id:
            if rec.product_id.id not in product_ids:
                result.append(rec)
                product_ids.append(rec.product_id.id)
        product_ids = []

        for rec in result:
            qs_line = self.env['quantity.survey.line'].search([('item','=',item),('project_id','=',project_id)])
            estimated_qty, estimated_cost = 0, 0
            for qs in qs_line:
                estimated_qty+=qs.current_qty*rec.planned_qty
                estimated_cost+=(qs.current_qty*rec.planned_qty)*rec.cost_unit
            actual_qty, actual_cost = self._get_actual_cost_actual_qty(item, project_id, rec.id)
            estimated_price = estimated_cost / estimated_qty if estimated_qty > 0 else 0
            actual_price = actual_cost / actual_qty if actual_qty > 0 else 0
            lines.append({
                'item_id': item,
                'project_id': project_id,
                'job_cost_item': rec.product_id.name,
                'product_id': rec.product_id,
                'estimated_cost': estimated_cost,
                'estimated_qty': estimated_qty,
                'estimated_price': estimated_price,
                'type_line': 'line',
                'actual_qty': actual_qty,
                'actual_price': actual_price,
                'actual_cost': actual_cost,
                'diffrence_qty': estimated_qty - actual_qty,
                'diffrence_price': estimated_price - actual_price,
                'diffrence_value': estimated_cost - actual_cost,
            })


        return lines
    def _get_subconstractor_of_item(self,item,project_id,lines):
        marterial_id = self.env['construction.subconstractor'].search([('item','=',item),('job_id.project_id','=',project_id)])
        estimated_qty, estimated_cost=0,0
        lst,product_ids=[],[]
        result, product_ids = [], []
        for rec in marterial_id:
            if rec.product_id.id not in product_ids:
                result.append(rec)
                product_ids.append(rec.product_id.id)
        product_ids = []

        for rec in result:
            qs_line = self.env['quantity.survey.line'].search([('item','=',item),('project_id','=',project_id)])
            estimated_qty, estimated_cost = 0, 0
            for qs in qs_line:
                estimated_qty+=qs.current_qty*rec.planned_qty
                estimated_cost+=(qs.current_qty*rec.planned_qty)*rec.cost_unit
            actual_qty, actual_cost = self._get_actual_cost_actual_qty(item, project_id, rec.id)
            estimated_price = estimated_cost / estimated_qty if estimated_qty > 0 else 0
            actual_price = actual_cost / actual_qty if actual_qty > 0 else 0
            lines.append({
                'item_id': item,
                'project_id': project_id,
                'job_cost_item': rec.product_id.name,
                'product_id': rec.product_id,
                'estimated_cost': estimated_cost,
                'estimated_qty': estimated_qty,
                'estimated_price': estimated_price,
                'type_line': 'line',
                'actual_qty': actual_qty,
                'actual_price': actual_price,
                'actual_cost': actual_cost,
                'diffrence_qty': estimated_qty - actual_qty,
                'diffrence_price': estimated_price - actual_price,
                'diffrence_value': estimated_cost - actual_cost,
            })


        return lines
    def _get_equipment_of_item(self,item,project_id,lines):
        marterial_id = self.env['construction.equipment'].search([('item','=',item),('job_id.project_id','=',project_id)])
        estimated_qty, estimated_cost=0,0
        lst,product_ids=[],[]
        result, product_ids = [], []
        for rec in marterial_id:
            if rec.product_id.id not in product_ids:
                result.append(rec)
                product_ids.append(rec.product_id.id)
        product_ids = []

        for rec in result:
            qs_line = self.env['quantity.survey.line'].search([('item','=',item),('project_id','=',project_id)])
            estimated_qty, estimated_cost = 0, 0
            for qs in qs_line:
                estimated_qty+=qs.current_qty*rec.planned_qty
                estimated_cost+=(qs.current_qty*rec.planned_qty)*rec.cost_unit
            actual_qty, actual_cost = self._get_actual_cost_actual_qty(item, project_id, rec.id)
            estimated_price = estimated_cost / estimated_qty if estimated_qty > 0 else 0
            actual_price = actual_cost / actual_qty if actual_qty > 0 else 0
            lines.append({
                'item_id': item,
                'project_id': project_id,
                'job_cost_item': rec.product_id.name,
                'product_id': rec.product_id,
                'estimated_cost': estimated_cost,
                'estimated_qty': estimated_qty,
                'estimated_price': estimated_price,
                'type_line': 'line',
                'actual_qty': actual_qty,
                'actual_price': actual_price,
                'actual_cost': actual_cost,
                'diffrence_qty': estimated_qty - actual_qty,
                'diffrence_price': estimated_price - actual_price,
                'diffrence_value': estimated_cost - actual_cost,
            })


        return lines




    def _get_product_move_item(self,project_id, key,pro_list,lines):

        stock_move = self.env['stock.move'].search([('item', '=', key),('project_id', '=', project_id),('product_id','not in',pro_list)])
        # job_cost_ids = self.env['construction.job.cost'].search([('item', '=', key), ('project_id', '=', project_id)])
        product_ids =[]
        actual_qty, actual_cost = 0, 0
        for rec in stock_move:
            if rec.product_id.id not in product_ids and rec.product_id:
                product_ids.append(rec.product_id.id)





        for rec in product_ids:
            produ_id = self.env['product.product'].search([('id', '=', rec)], limit=1)
            actual_qty, actual_cost = self._get_actual_cost_actual_qty(key, project_id, rec)
            estimated_price = 0
            actual_price = actual_cost / actual_qty if actual_qty > 0 else 0

            lines.append({
                'item_id': key,
                'project_id': project_id,
                'job_cost_item': produ_id.name,
                'product_id': produ_id,
                'estimated_cost': 0,
                'estimated_qty': 0,
                'estimated_price': estimated_price,
                'type_line': 'line',
                'actual_qty': actual_qty,
                'actual_price': actual_price,
                'actual_cost': actual_cost,
                'diffrence_qty':  actual_qty,
                'diffrence_price':  actual_price,
                'diffrence_value': actual_cost,


            })


        return lines
    def _get_etimate_cost_price(self,pro,key,project_id):
        job_cost_ids = self.env['construction.job.cost'].search(
            [('item', '=', key.id), ('project_id', '=', project_id)])
        estimated_qty, estimated_cost=0,0
        for rec in job_cost_ids:
             materials=self.env['construction.material'].search([('job_id','=',rec.id),('product_id','=',pro)])
             # if materials:
             #     for