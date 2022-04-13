from odoo import models, fields, api

class Deduction(models.Model):
    _name = 'contract.deduction.allowance'
    name = fields.Char("Name")
    account_id = fields.Many2one("account.account",string="Counterpart Account ")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    is_down_payment = fields.Boolean("Down Payment")
    type = fields.Selection([('deduction','Deduction'),('addition','Additional')],string="Type")
    sub_type = fields.Selection([('owner','Owner'),('supconstractor','sub contractor')],string="Type")

class DeductionLines(models.Model):
    _name = 'contract.deduction.allowance.lines'
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    name = fields.Many2one("contract.deduction.allowance",string="Name" ,domain="[('type','=',type),('sub_type','=',sub_type)]")
    account_id = fields.Many2one(related='name.account_id',string="Account ID")
    is_precentage = fields.Boolean("Is Precentage")
    precentage = fields.Float("Precentage")
    is_down_payment = fields.Float("Down Payment",compute='_calculate_down_payment',store=True,index=True)
    contract_id = fields.Many2one("construction.contract")
    move_id = fields.Many2one("account.move")


    @api.depends('precentage','contract_id.total_value')
    def _calculate_down_payment(self):
        for rec in self:
            rec.is_down_payment = (rec.precentage/100)*rec.contract_id.total_value
    @api.onchange('name')
    def _onchange_prectenage(self):
        self.is_precentage = self.name.is_precentage
        self.precentage = self.name.precentage


