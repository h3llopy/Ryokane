from odoo import api, fields, models, tools, _
from odoo.tools.translate import html_translate

class Page(models.Model):
    _inherit = 'website.page'

    show_popup = fields.Boolean(default=False)
    popup_title = fields.Char('Popup Title',translate=True)
    popup = fields.Html('Popup', translate=html_translate, sanitize_attributes=False)
