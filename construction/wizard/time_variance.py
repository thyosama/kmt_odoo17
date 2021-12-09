from datetime import datetime

from odoo import models, fields, api


class wizard(models.TransientModel):
    _name = 'time.variance'

    project_ids = fields.Many2many('project.project', 'project_ids', 'id')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def view_report(self):
        view_form = self.env.ref('construction.view_quantity_survey_line_tree')
        ids=[]
        for record in self.project_ids:
            for rec in record.tender_ids:
                quantity_servey = self.env['quantity.survey.line'].search([('tender_line','=',rec.id)],order='id desc',limit=1)

                if quantity_servey:
                    ids.append(quantity_servey.id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Time Variance',
            'view_mode': 'tree',
            'views': [(view_form.id, 'tree')],
            'res_model': 'quantity.survey.line',
            'domain': [('id', 'in',ids)],
            'target': 'current',

        }
