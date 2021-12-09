from odoo import api, fields, models 



class Test(models.Model):
    _name='construction.test'
    name = fields.Char(
        string='Name', 
        required=False)