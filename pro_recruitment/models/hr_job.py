from odoo import _, api, exceptions, fields, models


class HrJob(models.Model):
    _inherit = "hr.job"
    skills_ids = fields.One2many(comodel_name='hr.job.skills', inverse_name='job_id', string='Skills')
    education_grade_id = fields.Many2one('education.grade', string='Education grade')
    lang_grade_id = fields.Many2one('lang.grade', string='Language grade')
    experience_id = fields.Many2one('experience', string="Experience")
    gender = fields.Selection(string='Gender', selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('any', 'Any'),
    ])


class HrJobSkills(models.Model):
    _name = "hr.job.skills"

    job_id = fields.Many2one('hr.job')
    skill_id = fields.Many2one('hr.skill')
    skill_score = fields.Selection( string='Score',required=True, selection=[('1', '1'),('2', '2'), ('3', '3'), ('4', '4')])
    level = fields.Integer(string="Progress", help="Progress from zero knowledge (0%) to fully mastered (100%).")
    level_progress = fields.Integer(string="Progress", related='level')


class LangGrade(models.Model):
    _name = 'lang.grade'
    name = fields.Char(required=True)
    percentage = fields.Float('Percentage', required=True)


class Experience(models.Model):
    _name = 'experience'
    name = fields.Char(required=True)
    percentage = fields.Integer('Percentage', required=True)


class EducationGrade(models.Model):
    _name = 'education.grade'
    name = fields.Char(required=True)
    percentage = fields.Float('Percentage', required=True)