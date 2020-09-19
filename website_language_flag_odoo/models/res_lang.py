# -*- coding: utf-8 -*-
from odoo import fields, models


class ResLang(models.Model):
    _inherit = 'res.lang'

    flag_image = fields.Binary(string='Language Flag')
