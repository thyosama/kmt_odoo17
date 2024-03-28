from odoo import fields, models, api
from odoo import models, fields, api, _
import xlrd
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime


class DmsSheets(models.TransientModel):
    _name = 'tender.sheet.upload'

    file_name = fields.Binary('attach file')
    project_id = fields.Many2one("project.project")

    def get_cloumn_name(self, tech_name, value):

        model_id = self.env['ir.model'].sudo().search([('name', '=', 'construction.tender')])
        fields_nam = self.env['ir.model.fields'].sudo().search(
            [('model_id', '=', model_id.id), ('field_description', 'like', tech_name)], limit=1)
        value_id=''
        if fields_nam.ttype == 'many2one':
            value_id = self.env[fields_nam.relation].search([('name', '=', value)])
            if not value_id:
                value_id = self.env[fields_nam.relation].create({'name': value})
        return fields_nam.name,value_id

    def import_dms_file(self):
        # try:
        book = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_name))
        sheet = book.sheets()[0]

        trans_dic = {}
        sale_order = []

        data = []
        dict1 = {}
        print("Number of Rows: ", sheet.nrows)
        print("Number of Columns: ", sheet.ncols)
        related_job_ids=[]
        for row in range(1, sheet.nrows):
            dict1 = {}
            dict1['project_id']=self.project_id.id
            for col in range(0, sheet.ncols):

                colum_name,value_id = self.get_cloumn_name(sheet.cell_value(0, col), sheet.cell_value(row, col))
                if colum_name:

                    if value_id:
                        if colum_name == 'related_job' and value_id.id not in related_job_ids:
                            related_job_ids.append(value_id.id)
                        if not colum_name=='project_id':
                             dict1[colum_name] = value_id.id
                    else :
                        dict1[colum_name] = sheet.cell_value(row, col)
            data.append((dict1))

        for  job in related_job_ids:
            self.env['construction.tender'].create({
                'display_type':'line_section',
                'name':self.env['tender.related.job'].search([('id','=',job)]).name,
                'project_id':self.project_id.id
            })
            for line in data:
                if job==line['related_job']:
                    print(">>>>>>>>>>>>>>>>>>>>>>>.",line['related_job'],line)
                    self.env['construction.tender'].create(line)
