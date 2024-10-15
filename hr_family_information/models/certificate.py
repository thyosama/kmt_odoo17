from odoo import fields, models, api


class EmpCertificate(models.Model):
    _name = 'emp.certificate'
    _description = 'name'

    name = fields.Char(required=True)