from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update(reservation=ui_order.get("reservation"), practitioner=ui_order.get("practitioner"))
        return res

    practitioner = fields.Many2one(comodel_name="hr.employee", string="Practicienne")
    reservation = fields.Many2one(comodel_name='reservation', string="Reservation")
    salesman = fields.Many2one(comodel_name="hr.employee", string="Venduese", required=True, compute='_compute_salesman')

    @api.depends("session_id")
    def _compute_salesman(self):
        employee = self.env['hr.employee']
        for rec in self:
            user_id = rec.session_id.user_id.id
            emp = employee.search([('user_id', '=', user_id)], limit=1)
            rec.salesman = emp.id if emp else False


class Reservation(models.Model):
    _name = 'reservation'

    name = fields.Char(string="Reservation")
    reservation_analytic_tags = fields.Many2one('account.analytic.tag', string='Analytic Tags')
