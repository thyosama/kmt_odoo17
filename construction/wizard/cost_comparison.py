from datetime import datetime

from odoo import models, fields, api


class wizard(models.TransientModel):
    _name = 'cost.comparison'

    project_ids = fields.Many2one('project.project')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def view_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'project_ids': self.project_ids.id,


            },
        }
        return self.env.ref('construction.action_report_cost_comparison').report_action(self, data=data)
