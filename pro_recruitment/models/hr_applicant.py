import base64
from odoo import api, fields, models
from odoo.modules.module import get_module_resource


class HRApplicant(models.Model):
    _inherit = "hr.applicant"
    education_grade_id = fields.Many2one('education.grade', string='Education grade')
    lang_grade_id = fields.Many2one('lang.grade', string='Language grade')
    experience_id = fields.Many2one('experience', string="Experience")
    gender = fields.Selection(string='Gender', selection=[
        ('male', 'Male'),
        ('female', 'Female'),
    ])
    recommendation = fields.Html(string='Recommendation')
    @api.model
    def _default_image(self):
        image_path = get_module_resource('pro_recruitment', 'static/img', 'emp.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(default=_default_image)
    skills_ids = fields.One2many(comodel_name='hr.applicant.skills', inverse_name='applicant_id', string='Skills')

    @api.model
    def _search_is_skilled(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.is_skilled == 'skilled')
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    is_skilled = fields.Selection(
        string='Skilled ?',
        selection=[('not skilled', 'Not Skilled'),
                   ('skilled', 'Skilled')],
        default='not skilled', compute="compute_skilled_applicant", store=True, search=_search_is_skilled)

    is_selected = fields.Selection(
        string='Selected ?',
        selection=[('not selected', 'Not Selected'),
                   ('skilled', 'Selected')],
        default='not selected', compute="compute_selected_applicant", store=True, search=_search_is_skilled)

    @api.depends('skills_ids')
    def compute_skilled_applicant(self):
        for rec in self:
            if len(rec.skills_ids.ids) == len(rec.skills_ids.filtered(lambda x: x.skill_type == '1' ).ids):
                rec.is_skilled = 'skilled'
            else:
                rec.is_skilled = 'not skilled'

    @api.depends('gender', 'education_grade_id', 'lang_grade_id', 'experience_id')
    def compute_selected_applicant(self):
        for rec in self:
            rec.is_selected = 'not selected'
            for job in rec.job_id:
                if rec.gender == job.gender:
                    if rec.education_grade_id.percentage >= job.education_grade_id.percentage:
                        if rec.lang_grade_id.percentage >= job.lang_grade_id.percentage:
                            if rec.experience_id.percentage >= job.experience_id.percentage:
                                rec.is_selected = 'skilled'
    @api.model
    def create(self, vals):
        res = super(HRApplicant, self).create(vals)
        lines = []
        for line in res.job_id.skills_ids:
            new = self.env['hr.applicant.skills'].create({
                'applicant_id': res.id,
                'job_position_skill_id': line.id,
                'skill_id': line.skill_id.id,
                'skill_score': False,
            })
            new.change_level()
            lines.append(new.id)
        res.skills_ids = [(6, 0, lines)]
        return res

    @api.onchange('job_id')
    def _onchange_job_id(self):
        for rec in self:
            lines = []
            for line in rec.job_id.skills_ids:
                new = self.env['hr.applicant.skills'].create({
                    'applicant_id': rec.id,
                    'job_position_skill_id': line.id,
                    'skill_id': line.skill_id.id,
                    'skill_score': False,
                    # 'job_skill_level': line.level,
                })
                new.change_level()
                lines.append(new.id)
            rec.skills_ids = [(6, 0, lines)]


class HrApplicantSkills(models.Model):
    _name = "hr.applicant.skills"

    applicant_id = fields.Many2one('hr.applicant')
    skill_id = fields.Many2one('hr.skill')
    hr_job_skill_id = fields.Many2one('hr.job.skills')
    skill_score = fields.Selection( string='Skill Score', selection=[('1', '1'),('2', '2'), ('3', '3'), ('4', '4')])
    job_position_skill_id = fields.Many2one('hr.job.skills')
    position_skill_score = fields.Selection( related='job_position_skill_id.skill_score', string="Position Skill")
    job_skill_level = fields.Integer(string="Job Skill Level")
    level = fields.Integer(string="Progress", help="Progress from zero knowledge (0%) to fully mastered (100%).")
    level_progress = fields.Integer(string="Progress", related='level')
    skill_type = fields.Selection(string='Skill_type', selection=[('0', 'Un Skilled'),('1', 'Skilled')])

    @api.onchange('skill_score')
    def change_level(self):
        self.skill_type = '0'
        if int(self.skill_score) >= int(self.job_position_skill_id.skill_score):
            self.skill_type = '1'
