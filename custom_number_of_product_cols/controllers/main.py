from odoo.addons.website_sale.controllers.main import WebsiteSale
main.PPG = 18 # Products per Page
main.PPR = 3 # Products per Row

class WebsiteSale(WebsiteSale):
def _get_search_order(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        return 'is_published desc, %s, id desc, website_sequence ASC' % post.get('order')