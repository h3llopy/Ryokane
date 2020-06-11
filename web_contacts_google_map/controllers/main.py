# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, route


class PaymentPortal(http.Controller):

	@http.route('/find_us_on_map', type='http', auth="public", website=True)
	def find_us_on_map(self, **kwargs):
		map_api_key = request.env['ir.config_parameter'].sudo().get_param('website.google_maps_api_key')
		partner_ids = request.env['res.partner'].search([('show_on_find_us_map','=',True)])
		google_maps_api_key = request.website.google_maps_api_key
		values = {}
		if google_maps_api_key:
			values.update({'map_api_key' : google_maps_api_key,})
		values.update({'partner_ids' : partner_ids,})
		return request.render("web_contacts_google_map.find_us_on_map_view_template", values)


	@http.route('/show_partner_mails', type='json', auth='public', website=True)
	def show_partner_mails(self, **kw):
		partner_ids = request.env['res.partner'].search([('show_on_find_us_map','=',True)])
		address = []
		for partner_id in partner_ids:
			address_detais = partner_id.street or '' + ', ' + partner_id.city or '' + ', ' + partner_id.state_id.name or ''+ ' ' + partner_id.zip or ''+ ', ' + partner_id.country_id.name or ''+ ' '
			partner_name = partner_id.name
			temp_address = []
			temp_address.append(partner_name)
			temp_address.append(address_detais)
			temp_address.append(partner_id.partner_latitude)
			temp_address.append(partner_id.partner_longitude)
			address.append(temp_address)
		return {
			'address' : address,
		}
		