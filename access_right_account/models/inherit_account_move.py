from odoo import models, fields, api
from lxml import etree
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import ast
import json

class InheritAccoun(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        # print(view_id)
        # print(view_type)
        # print(options)
        # print(self.env.user.has_group("access_right_account.account_move_group"))
        res=super().get_view(view_id, view_type, **options)
        journal_action_tree=self.env.ref('account.action_move_journal_line').id
        journal_action_form=self.env.ref('account.action_move_journal_line').id
        invoice_action_tree=self.env.ref('account.action_move_out_invoice_type').id
        invoice_action_form=self.env.ref('account.action_move_out_invoice_type').id
        if view_type == 'tree' and not self.env.user.has_group("access_right_account.journal_move_group") and options["action_id"]==journal_action_tree:
            doc = etree.XML(res['arch'])
            tree = doc.xpath("//tree")
            if tree:
                tree[0].set("create", "false")
                tree[0].set("delete", "false")
                res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form' and not self.env.user.has_group("access_right_account.journal_move_group") and options["action_id"]==journal_action_form:
            doc = etree.XML(res['arch'])
            form = doc.xpath("//form")
            if form:
                form[0].set("create", "false")
                form[0].set("delete", "false")
                res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'tree' and not self.env.user.has_group("access_right_account.invoice_move_group") and options["action_id"]==invoice_action_tree:
            doc = etree.XML(res['arch'])
            tree = doc.xpath("//tree")
            if tree:
                tree[0].set("create", "false")
                tree[0].set("delete", "false")
                res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form' and not self.env.user.has_group("access_right_account.invoice_move_group") and options["action_id"]==invoice_action_form:
            doc = etree.XML(res['arch'])
            form = doc.xpath("//form")
            if form:
                form[0].set("create", "false")
                form[0].set("delete", "false")
                res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


