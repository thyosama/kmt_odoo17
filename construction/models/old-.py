from odoo import models, fields, api
# class AllowDeductionLines(models.Model):
#     _name = 'contract.deduction.addition.lines.invoice'
#     type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
#     sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'supconstractor')], string="Type")
#     name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
#     account_id = fields.Many2one(related='name.account_id',string="Account ID")
#     is_precentage = fields.Boolean("Is Precentage")
#     precentage = fields.Float("Precentage")
#     value = fields.Float("Total Value",compute='_calculate_down_payment')
#     invoice_id = fields.Many2one("account.invoice")
#     last_value = fields.Float("Last Value",compute='get_last_value')
#     current_value = fields.Float("Current Value",compute='_get_current_value')
#
#     @api.depends('invoice_id.contract_id')
#     def get_last_value(self):
#         for rec in self:
#             rec.last_value =0
#             invoice_ids = self.env['account.invoice'].search([('contract_id','=',rec.invoice_id.contract_id.id)])
#             last_v=0
#             for inv in invoice_ids:
#                 last_v+=inv.last_total_value
#             rec.last_value=last_v
#     @api.depends('last_value','value')
#     def _get_current_value(self):
#         for rec in self:
#             rec.current_value = rec.value - rec.last_value
#
#
#
#     @api.depends('precentage','invoice_id.total_value')
#     def _calculate_down_payment(self):
#         for rec in self:
#             if rec.is_precentage==True:
#                 rec.value = (rec.precentage/100)*rec.invoice_id.total_value
#             else:
#                 rec.value = rec.precentage
#
#     @api.onchange('name')
#     def _onchange_prectenage(self):
#         self.is_precentage = self.name.is_precentage
#         self.precentage = self.name.precentage

class DeductionLines(models.Model):
    _name = 'contract.deduction.lines.invoice'
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
    account_id = fields.Many2one(related='name.account_id',string="Account ID")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    value = fields.Float("Total Value",compute='_calculate_down_payment')
    invoice_id = fields.Many2one("account.invoice")
    move_id = fields.Many2one("account.move")
    last_value = fields.Float("Previous Value",compute='get_last_value')
    current_value = fields.Float("Current Value",compute='_get_current_value')

    @api.depends('invoice_id.contract_id','move_id.contract_id','invoice_id')
    def get_last_value(self):
        for rec in self:
            rec.last_value =0
            invoice_ids = self.env['account.invoice'].search([('contract_id','=',rec.invoice_id.contract_id.id)])
            last_v=0
            for inv in invoice_ids:
                last_v+=inv.last_total_value
            rec.last_value=last_v
    @api.depends('last_value','value')
    def _get_current_value(self):
        for rec in self:
            rec.current_value = rec.value - rec.last_value



    @api.depends('precentage','invoice_id.total_value')
    def _calculate_down_payment(self):
        for rec in self:
            if rec.is_precentage==True:
                rec.value = (rec.precentage/100)*rec.invoice_id.total_value
            else:
                rec.value = rec.precentage

    @api.onchange('name')
    def _onchange_prectenage(self):
        self.is_precentage = self.name.is_precentage
        self.precentage = self.name.precentage

class AdditionLines(models.Model):
    _name = 'contract.addition.lines.invoice'
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
    account_id = fields.Many2one(related='name.account_id',string="Account ID")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    value = fields.Float("Total Value",compute='_calculate_down_payment')
    invoice_id = fields.Many2one("account.invoice")
    last_value = fields.Float("Previous Value",compute='get_last_value')
    current_value = fields.Float("Current Value",compute='_get_current_value')

    @api.depends('invoice_id.contract_id')
    def get_last_value(self):
        for rec in self:
            rec.last_value =0
            invoice_ids = self.env['account.invoice'].search([('contract_id','=',rec.invoice_id.contract_id.id)])
            last_v=0
            for inv in invoice_ids:
                last_v+=inv.last_total_value
            rec.last_value=last_v
    @api.depends('last_value','value')
    def _get_current_value(self):
        for rec in self:
            rec.current_value = rec.value - rec.last_value



    @api.depends('precentage','invoice_id.total_value')
    def _calculate_down_payment(self):
        for rec in self:
            if rec.is_precentage==True:
                rec.value = (rec.precentage/100)*rec.invoice_id.total_value
            else:
                rec.value = rec.precentage

    @api.onchange('name')
    def _onchange_prectenage(self):
        self.is_precentage = self.name.is_precentage
        self.precentage = self.name.precentage




##################################################3
from odoo import models, fields, api
# class AllowDeductionLines(models.Model):
#     _name = 'contract.deduction.addition.lines.invoice'
#     type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
#     sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'supconstractor')], string="Type")
#     name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
#     account_id = fields.Many2one(related='name.account_id',string="Account ID")
#     is_precentage = fields.Boolean("Is Precentage")
#     precentage = fields.Float("Precentage")
#     value = fields.Float("Total Value",compute='_calculate_down_payment')
#     invoice_id = fields.Many2one("account.invoice")
#     last_value = fields.Float("Last Value",compute='get_last_value')
#     current_value = fields.Float("Current Value",compute='_get_current_value')
#
#     @api.depends('invoice_id.contract_id')
#     def get_last_value(self):
#         for rec in self:
#             rec.last_value =0
#             invoice_ids = self.env['account.invoice'].search([('contract_id','=',rec.invoice_id.contract_id.id)])
#             last_v=0
#             for inv in invoice_ids:
#                 last_v+=inv.last_total_value
#             rec.last_value=last_v
#     @api.depends('last_value','value')
#     def _get_current_value(self):
#         for rec in self:
#             rec.current_value = rec.value - rec.last_value
#
#
#
#     @api.depends('precentage','invoice_id.total_value')
#     def _calculate_down_payment(self):
#         for rec in self:
#             if rec.is_precentage==True:
#                 rec.value = (rec.precentage/100)*rec.invoice_id.total_value
#             else:
#                 rec.value = rec.precentage
#
#     @api.onchange('name')
#     def _onchange_prectenage(self):
#         self.is_precentage = self.name.is_precentage
#         self.precentage = self.name.precentage

class DeductionLines(models.Model):
    _name = 'contract.deduction.lines.invoice'
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
    account_id = fields.Many2one(related='name.account_id',string="Account ID")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    value = fields.Float("Total Value",compute='_calculate_down_payment')
    invoice_id = fields.Many2one("account.invoice")
    move_id = fields.Many2one("account.move")
    last_value = fields.Float("Last Value",compute='get_last_value')
    current_value = fields.Float("Current Value",compute='_get_current_value')

    @api.depends('move_id.contract_id')
    def get_last_value(self):
        for rec in self:
            rec.last_value =0
            invoice_ids = self.env['account.move'].search([('contract_id','=',rec.move_id.contract_id.id)])
            last_v=0
            for inv in invoice_ids:
                last_v+=inv.last_total_value
            rec.last_value=last_v
    @api.depends('last_value','value')
    def _get_current_value(self):
        for rec in self:
            rec.current_value = rec.value - rec.last_value



    @api.depends('precentage','move_id.total_value')
    def _calculate_down_payment(self):
        for rec in self:
            if rec.is_precentage==True:
                rec.value = (rec.precentage/100)*rec.invoice_id.total_value
            else:
                rec.value = rec.precentage

    @api.onchange('name')
    def _onchange_prectenage(self):
        self.is_precentage = self.name.is_precentage
        self.precentage = self.name.precentage

class AdditionLines(models.Model):
    _name = 'contract.addition.lines.invoice'
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'supconstractor')], string="Type")
    name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
    account_id = fields.Many2one(related='name.account_id',string="Account ID")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    value = fields.Float("Total Value",compute='_calculate_down_payment')
    move_id = fields.Many2one("account.move")
    invoice_id = fields.Many2one("account.invoice")
    last_value = fields.Float("Last Value",compute='get_last_value')
    current_value = fields.Float("Current Value",compute='_get_current_value')

    @api.depends('move_id.contract_id')
    def get_last_value(self):
        for rec in self:
            rec.last_value = 0
            invoice_ids = self.env['account.move'].search([('contract_id', '=', rec.move_id.contract_id.id)])
            last_v = 0
            for inv in invoice_ids:
                last_v += inv.last_total_value
            rec.last_value = last_v

    @api.depends('last_value', 'value')
    def _get_current_value(self):
        for rec in self:
            rec.current_value = rec.value - rec.last_value

    @api.depends('precentage', 'move_id.total_value')
    def _calculate_down_payment(self):
        for rec in self:
            if rec.is_precentage == True:
                rec.value = (rec.precentage / 100) * rec.invoice_id.total_value
            else:
                rec.value = rec.precentage

    @api.onchange('name')
    def _onchange_prectenage(self):
        self.is_precentage = self.name.is_precentage
        self.precentage = self.name.precentage


