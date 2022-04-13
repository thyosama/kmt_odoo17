from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import ValidationError


class ParentProject(models.Model):
    _name = "parent.project"
    name = fields.Char()


class Project(models.Model):
    _inherit = "project.project"

    parent_project_id = fields.Many2one("parent.project", string="Parent")
    parent_id = fields.Many2one("project.project", string="Parent") #todo remove it if you can :)