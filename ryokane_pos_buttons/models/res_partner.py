from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    birthday = fields.Date(string="Birthday")



class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    practitioner = fields.Many2one(comodel_name="hr.employee", string="Practicienne", readonly=True)
    reservation = fields.Many2one(comodel_name='reservation', string="Reservation", readonly=True)
    salesman = fields.Many2one(comodel_name="hr.employee", string="Salesman", required=False, readonly=True)

    def _group_by(self):
        return """
            GROUP BY
                s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                s.user_id, s.location_id, s.company_id, s.sale_journal,
                s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                s.practitioner, s.reservation, s.salesman,
                l.product_id,
                pt.categ_id, pt.pos_categ_id,
                p.product_tmpl_id,
                ps.config_id
        """

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                SUM(l.qty) AS product_qty,
                SUM(l.qty * l.price_unit) AS price_sub_total,
                SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.practitioner as practitioner,
                s.reservation as reservation,
                s.salesman as salesman,
                s.state AS state,
                s.user_id AS user_id,
                s.location_id AS location_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.invoice_id IS NOT NULL AS invoiced
        """

   