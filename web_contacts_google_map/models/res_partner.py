from odoo import fields,models


class ResPartner(models.Model):
	_inherit = 'res.partner'

	show_on_find_us_map = fields.Boolean(
		string="Show on find us map",
		copy=False,
	)