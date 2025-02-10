# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import html2plaintext, is_html_empty



class ReportHeaderFooter(models.Model):
    _name = 'report.header.footer'
    _description = 'Report Header and Footer Templates'

    name = fields.Char(string="Template Name", required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    logo_custom = fields.Binary( string="Custom Logo")
    report_header_custom = fields.Html(string="Custom Header")
    report_footer_custom = fields.Html(
        string="Custom Footer", default=lambda self: "<p>Default Footer Content</p>"
    )

    company_details_custom = fields.Html(string='Company Details', related='company_id.company_details_custom', readonly=False,
                                  default="Add Company Details")
    is_company_details_custom_empty = fields.Boolean(compute='_compute_empty_company_details_custom')

    @api.depends('company_details_custom')
    def _compute_empty_company_details_custom(self):
        # In recent change when an html field is empty a <p> balise remains with a <br> in it,
        # but when company details is empty we want to put the info of the company
        for record in self:
            record.is_company_details_custom_empty = not html2plaintext(record.company_details_custom or '')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    header_footer_template_id = fields.Many2one(
        'report.header.footer', string='Header/Footer Template',
        domain = "[('company_id', '=', company_id)]",)

class ResCompany(models.Model):
    _inherit = "res.company"

    logo_custom = fields.Binary(string="Custom Logo")
    report_header_custom = fields.Html(string="Custom Header")
    report_footer_custom = fields.Html(
        string="Custom Footer", default=lambda self: "<p>Default Footer Content</p>"
    )
    company_details_custom = fields.Html(string='Company Details', readonly=False,
                                  default="Add Company Details")

    header_footer_template_ids = fields.One2many(
        'report.header.footer', 'company_id', string='Header/Footer Templates'
    )

    header_footer_template_id = fields.Many2one('ir.ui.view', 'Document Template')

    company_details_custom = fields.Html(string='Company Details',
                                         readonly=False,
                                         default="Add Company Details")
    is_company_details_custom_empty = fields.Boolean(compute='_compute_empty_company_details_custom')

    @api.depends('company_details_custom')
    def _compute_empty_company_details_custom(self):
        # In recent change when an html field is empty a <p> balise remains with a <br> in it,
        # but when company details is empty we want to put the info of the company
        for record in self:
            record.is_company_details_custom_empty = not html2plaintext(record.company_details_custom or '')
