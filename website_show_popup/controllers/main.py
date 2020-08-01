import odoo
from odoo import http, models, fields, _
from odoo.http import request

class WesiteShowPopup(http.Controller):

    @http.route(['/website/website_show_popup'], type='json', auth="public", website=True)
    def multi_render(self, model,page_id):
        page = request.env['website.page'].sudo().search([('id','=',page_id)],limit=1)
        if page.id == page_id:
            if page.show_popup:
                return {                
                    'title':page.popup_title or '',
                    'popup' : page.popup or '',
                }
            else:
                return False