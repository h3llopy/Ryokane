from odoo import models, fields, api

from dateutil.relativedelta import relativedelta

class GiftCard(models.Model):
    _inherit = "aspl.gift.card"
    _description = "Gift Card"

    card_no = fields.Char(readonly=False)

    expire_date = fields.Date(default=lambda self: fields.Date.today() + relativedelta(years=1))


