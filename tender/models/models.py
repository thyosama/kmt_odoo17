from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'tender.related.job'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
