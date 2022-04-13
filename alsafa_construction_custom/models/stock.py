from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Stock(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        if self.picking_type_id.code=='internal' and \
               not self.env.user.has_group('alsafa_construction_custom.create_internal_transfer'):
                raise ValidationError("You Cann't create Internal Transfer ")
        res =super(Stock, self).button_validate()
        return res





    # @api.onchange('picking_type_id')
    # def _onchange_picking_type_id_test(self):
    #     if self.picking_type_id.code=='internal' and \
    #        not self.env.user.has_group('giza_masr_custom.create_internal_transfer'):
    #         raise ValidationError("You Cann't create Internal Transfer ")

