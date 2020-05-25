# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request, route
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class WebsiteSlides(WebsiteSlides):

	def sitemap_slide(env, rule, qs):
		Channel = env['slide.channel']
		dom = sitemap_qs2dom(qs=qs, route='/slides/', field=Channel._rec_name)
		dom += env['website'].get_current_website().website_domain()
		for channel in Channel.search(dom):
			loc = '/slides/%s' % slug(channel)
			if not qs or qs.lower() in loc:
				yield {'loc': loc}

	@http.route([
        '''/slides/<model("slide.channel"):channel>''',
        '''/slides/<model("slide.channel"):channel>/page/<int:page>''',

        '''/slides/<model("slide.channel"):channel>/<string:slide_type>''',
        '''/slides/<model("slide.channel"):channel>/<string:slide_type>/page/<int:page>''',

        '''/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>''',
        '''/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>''',

        '''/slides/<model("slide.channel"):channel>/category/<model("slide.category"):category>''',
        '''/slides/<model("slide.channel"):channel>/category/<model("slide.category"):category>/page/<int:page>''',

        '''/slides/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>''',
        '''/slides/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>/page/<int:page>'''],
        type='http', auth="public", website=True, sitemap=sitemap_slide)
	def channel(self, channel, category=None, tag=None, page=1, slide_type=None, sorting='creation', search=None, **kw):
		if not channel.can_access_from_current_website():
			raise werkzeug.exceptions.NotFound()

		user = request.env.user
		Slide = request.env['slide.slide']
		domain = [('channel_id', '=', channel.id)]
		if channel.visibility == 'private':
			domain += [('allow_channel_partner_ids.partner_id','=',user.partner_id.id)]

		pager_url = "/slides/%s" % (channel.id)
		pager_args = {}

		if search:
			domain += [
				'|', '|',
				('name', 'ilike', search),
				('description', 'ilike', search),
				('index_content', 'ilike', search)]
			pager_args['search'] = search
		else:
			if category:
				domain += [('category_id', '=', category.id)]
				pager_url += "/category/%s" % category.id
			elif tag:
				domain += [('tag_ids.id', '=', tag.id)]
				pager_url += "/tag/%s" % tag.id
			if slide_type:
				domain += [('slide_type', '=', slide_type)]
				pager_url += "/%s" % slide_type

		if not sorting or sorting not in self._order_by_criterion:
			sorting = 'date'
		order = self._order_by_criterion[sorting]
		pager_args['sorting'] = sorting

		pager_count = Slide.search_count(domain)
		pager = request.website.pager(url=pager_url, total=pager_count, page=page,
                                      step=self._slides_per_page, scope=self._slides_per_page,
                                      url_args=pager_args)
		slides = Slide.search(domain, limit=self._slides_per_page, offset=pager['offset'], order=order)
		print(":slides",slides)
		values = {
			'channel': channel,
			'category': category,
			'slides': slides,
			'tag': tag,
			'slide_type': slide_type,
			'sorting': sorting,
			'user': user,
			'pager': pager,
			'is_public_user': user == request.website.user_id,
			'display_channel_settings': not request.httprequest.cookies.get('slides_channel_%s' % (channel.id), False) and channel.can_see_full,
		}
		if search:
			values['search'] = search
			return request.render('website_slides.slides_search', values)

        # Display uncategorized slides
		if not slide_type and not category:
			category_datas = []
			for category in Slide.read_group(domain, ['category_id'], ['category_id']):
				category_id, name = category.get('category_id') or (False, _('Uncategorized'))
				category_datas.append({
					'id': category_id,
					'name': name,
					'total': category['category_id_count'],
					'slides': Slide.search(category['__domain'], limit=4, offset=0, order=order)
				})
			values.update({
				'category_datas': category_datas,
			})
		return request.render('website_slides.home', values)
