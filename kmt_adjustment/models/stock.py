# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], string="Type", readonly=True)

    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm',
        help='International Commercial Terms are a series of predefined commercial terms used in international transactions.')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    shipment = fields.Char('Shipment No')
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm',
        help='International Commercial Terms are a series of predefined commercial terms used in international transactions.')

    registration_ids = fields.Many2many(comodel_name='registration.number',  string='Registration Number')
    sid_ids = fields.Many2many(comodel_name='s.id',  string='S-ID')


class RegistrationNumber(models.Model):
    _name = "registration.number"
    name = fields.Char('Registration Number')


class SID(models.Model):
    _name = "s.id"
    name = fields.Char('Name')
