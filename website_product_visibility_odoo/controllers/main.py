# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class website_sale_product(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        category = request.env['product.public.category']
        category = Category.search([('id', '=', int(category))], limit=1)
        if category and not category.can_access_from_current_website():
            raise NotFound()
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if category:
            category = request.env['product.public.category'].sudo().search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        ################
#         if request.env.user.partner_id.visible_product_ids:
#             for visible_product in request.env.user.partner_id.visible_product_ids:
#                 visible_product_ids.append(visible_product.id)
#         if request.env.user.partner_id.visible_audience_ids:
#             for categ in request.env.user.partner_id.visible_audience_ids:
#                 products = request.env['product.template'].sudo().search([('categ_id', '=', categ.id)])
#                 for product in products:
#                     visible_product_ids.append(product.id)
#         if public_prod_categ:
#             public_partner=request.env.ref('base.public_partner')
#             if public_partner.visible_product_ids:
#                 for visible_product in public_partner.visible_product_ids:
#                     visible_product_ids.append(visible_product.id)
            
        if request.env.user.partner_id:
            visible_product_ids = []
            public_prod_categ = request.env['ir.config_parameter'].sudo().get_param('website_product_visibility_odoo.visible_public_prod_categ_too')
            if request.env.user.partner_id.visible_product_ids:
                visible_product_ids += request.env.user.partner_id.visible_product_ids.ids
            if request.env.user.partner_id.visible_audience_ids:
                visible_product_ids += request.env['product.template'].sudo().search([('audience_id', 'in', request.env.user.partner_id.visible_audience_ids.ids)]).ids
            if public_prod_categ:
                public_partner = request.env.ref('base.public_partner')
                if public_partner.sudo().visible_product_ids:
                    visible_product_ids += public_partner.sudo().visible_product_ids.ids
                if public_partner.sudo().visible_audience_ids:
                    visible_product_ids += request.env['product.template'].sudo().search(
                        [('audience_id', 'in', public_partner.sudo().visible_audience_ids.ids)]).ids

            visible_product_ids = list(set(visible_product_ids))
            domain += [('id', 'in', visible_product_ids)]
        ##############
        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].sudo()
        Category = request.env['product.public.category'].sudo()
        search_categories = False
        if search:
            categories = Product.search(domain).mapped('public_categ_ids')
            search_categories = Category.search([('id', 'parent_of', categories.ids)] + request.website.website_domain())
            categs = search_categories.filtered(lambda c: not c.parent_id)
        else:
            categs = Category.search([('parent_id', '=', False)] + request.website.website_domain())

        parent_category_ids = []
        if category:
            url = "/shop/category/%s" % slug(category)
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute'].sudo()
        if products:
            # get all products without limit
            selected_products = Product.search(domain, limit=False)
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            'search_categories_ids': search_categories and search_categories.ids,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)
