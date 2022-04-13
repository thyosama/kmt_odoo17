from odoo import fields, models, api


class ProjectTax(models.Model):
    _name = 'project.type.tax'
    _description = 'Project State Taxes'

    name = fields.Char(required=True)



class Project (models.Model):
    _inherit = 'project.project'
    type_tax_id = fields.Many2one("project.type.tax",string="حاله الضريبه علي المشروع")
