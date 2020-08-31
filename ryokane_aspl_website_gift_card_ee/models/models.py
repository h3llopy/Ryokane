# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class ryokane_aspl_website_gift_card_ee(models.Model):
#     _name = 'ryokane_aspl_website_gift_card_ee.ryokane_aspl_website_gift_card_ee'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
