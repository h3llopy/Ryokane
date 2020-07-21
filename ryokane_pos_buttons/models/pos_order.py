from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update(reservation=ui_order.get("reservation"), practitioner=ui_order.get("practitioner"), salesman=ui_order.get("salesperson"))
        return res

    practitioner = fields.Many2one(comodel_name="hr.employee", string="Practicienne")
    reservation = fields.Many2one(comodel_name='reservation', string="Reservation")
    salesman = fields.Many2one(comodel_name="hr.employee", string="Salesman", required=False)



class Reservation(models.Model):
    _name = 'reservation'

    name = fields.Char(string="Reservation")
    reservation_analytic_tags = fields.Many2one('account.analytic.tag', string='Analytic Tags')
