from odoo import models, fields, api

class GiftCard(models.Model):
    _inherit = "aspl.gift.card"
    _description = "Gift Card"

    card_no = fields.Char(readonly=False)

