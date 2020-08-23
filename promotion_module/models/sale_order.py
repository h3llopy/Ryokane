from dateutil import parser
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SalesClass(models.Model):
    _inherit = 'sale.order'
#    _name= 'sale.order'

    def _put_reward_values_product(self, program):
        _logger.info('WAFI: put reward values product')
        #price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_unit

        #order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._is_valid_product(x.product_id))
        reward_qty= program.reward_product_quantity
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.reward_product_id.id,
            'product_uom_qty': reward_qty,
            'name': program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }
