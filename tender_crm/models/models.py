# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'
    lead_id = fields.Many2one("crm.lead")
class tender_crm(models.Model):
    _inherit = 'crm.lead'
    is_project = fields.Boolean()
    is_count_project = fields.Integer(compute='get_is_count_project')

    def get_is_count_project(self):
        for rec in self:
            rec.is_count_project=0
            if rec.id:
                project_id = self.env['project.project'].search([('lead_id','=',self.id)])
                rec.is_count_project=len(project_id)



    def create_project(self):
        project_id = self.env['project.project']
        self.is_project=True
        # project_id.create({
        #     'name':self.name,
        #     'type':'draft',
        #     'lead_id':self.id,
        #     'partner_id':self.partner_id.id if self.partner_id else False,
        #
        # })

        action = self.env["ir.actions.actions"]._for_xml_id("tender.action_crm_project")
        action['context'] = {

            'default_name':self.name,
            'default_type':'draft',
            'default_lead_id':self.id,
            'default_partner_id':self.partner_id.id if self.partner_id else False,

        }

        return action


    def action_view_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects ',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'domain': [('lead_id', '=', self.id)],
            'target': 'current',

        }
