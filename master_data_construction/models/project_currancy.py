from odoo import fields, models, api


class ModelName(models.Model):
    _name = "project.currency"
    currancy_id = fields.Many2one("res.currency")
    ratio = fields.Float(default=1)
    project_id = fields.Many2one("project.project")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
