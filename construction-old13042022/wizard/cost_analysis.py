

from odoo import models, fields, api


class wizard(models.TransientModel):
    _name = 'cost.analysis.wizard'

    project_ids = fields.Many2one('project.project')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def get_cost_analysis(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cost Analysis',
            'view_mode': 'tree',
            'res_model': 'cost.analysis.report',
            'domain': [('project_id', 'in', self.project_ids.ids)],
            'target': 'current',

        }