# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import requests
from PIL import Image

import base64
import datetime
import io
import json
import re

from werkzeug import urls

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools import image
from odoo.tools.translate import html_translate
from odoo.exceptions import Warning
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for
# from moviepy.editor import VideoFileClip
import os
import cv2

class Channel(models.Model):
    """ A channel is a container of slides. It has group-based access configuration
    allowing to configure slide upload and access. Slides can be promoted in
    channels. """
    _inherit = 'slide.channel'

    @api.depends('slide_ids.slide_type', 'slide_ids.website_published','slide_ids.allow_channel_partner_ids')
    def _count_presentations(self):
        result = dict.fromkeys(self.ids, dict())
        if self.visibility == 'private':
            res = self.env['slide.slide'].read_group(
            [('website_published', '=', True), ('channel_id', 'in', self.ids),
            ('allow_channel_partner_ids.partner_id','=',self.env.user.partner_id.id)],
            ['channel_id', 'slide_type'], ['channel_id', 'slide_type'],
            lazy=False)
        else:
            res = self.env['slide.slide'].read_group(
            [('website_published', '=', True), ('channel_id', 'in', self.ids)],
            ['channel_id', 'slide_type'], ['channel_id', 'slide_type'],
            lazy=False)

        for res_group in res:
            result[res_group['channel_id'][0]][res_group['slide_type']] = result[res_group['channel_id'][0]].get(res_group['slide_type'], 0) + res_group['__count']
        for record in self:
            record.nbr_presentations = result[record.id].get('presentation', 0)
            record.nbr_documents = result[record.id].get('document', 0)
            record.nbr_videos = result[record.id].get('video', 0)
            record.nbr_infographics = result[record.id].get('infographic', 0)
            record.total = record.nbr_presentations + record.nbr_documents + record.nbr_videos + record.nbr_infographics

    
class AllowChannelPartner(models.Model):
    _name = 'allow.channel.partner'

    partner_id = fields.Many2one('res.partner',string="Partner")
    slide_id = fields.Many2one('slide.slide',string="Slide")
    

class SlideInherit(models.Model):
    _inherit = 'slide.slide'
    
    is_local_url = fields.Boolean('Use Local Video', help="Use attachments local video.",default=False)
    local_url = fields.Many2one('ir.attachment','Local Video', help="Videos attachments in slide.slide object.",domain="[('mimetype', 'like', 'video/'), ('res_model', '=', 'slide.channel'),('res_id','=',channel_id)]")
    allow_channel_partner_ids = fields.One2many('allow.channel.partner','slide_id',string="Allow Channel Partner Ids")

    def remove_local_video(self):
        video_path = "/tmp/local_video_v12"
        if os.path.exists(video_path):
            os.system("rm -r "+video_path)
    
    @api.onchange('is_local_url')
    def _on_change_is_local_url(self):
        self.ensure_one()
        if self.is_local_url:
            self.url = False
        else:
            self.local_url = False
     
    @api.onchange('local_url')
    def _on_change_local_url(self):
        self.ensure_one()
        if self.local_url:
            self.document_id = False
            self.slide_type = 'video'
            video_name = self.local_url.name
            fist_name = video_name.split('.')
            if fist_name:
                self.name = fist_name[0]
            self.description = self.local_url.description
            self.mime_type = self.local_url.mimetype
             
            if os.path.exists("/tmp"):
                video_path = "/tmp/local_video_v12"
                if not os.path.exists(video_path):
                    try:
                        os.mkdirs(video_path)
                    except Exception as e:
                        try:
                            os.makedirs(video_path)
                        except:
                            raise UserError("Error while creating PATH directory")
                if os.path.exists(video_path):
                    os.system('chmod -R 777 '+video_path)
                video_path = "/tmp/local_video_v12/"+self.local_url.name
                if not os.path.exists(str(video_path)):
                    with open(video_path, 'wb+') as f:
                        img = bytes(self.local_url.datas)
                        img = img[img.find(b',')+1:]
                        f.write(base64.standard_b64decode(img))
                if os.path.exists(video_path):
#                     clip = VideoFileClip(video_path)
#                     self.completion_time = clip.duration/3600
                    cam = cv2.VideoCapture(video_path)
                    ret,frame = cam.read()
                    if ret:
                        im_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        imh_path = "/tmp/local_video_v12/video_img_v12.jpg"
                        cv2.imwrite(imh_path, im_bgr)
                        if os.path.exists(imh_path):
                            img_file = open(imh_path, 'rb+')
                            if img_file:
                                image_base64 = base64.b64encode(img_file.read())
                                if image_base64:
                                    self.image = image_base64
    
    @api.model
    def create(self, values):
        if values.get('local_url'):
            slide_id = self.env['ir.attachment'].search([('id', '=', int(values.get('local_url')))])
            if slide_id:
                values.update({'slide_type':'video',
                               'mime_type':slide_id.mimetype,
                               })
                imh_path = "/tmp/local_video_v12/video_img_v12.jpg"
                if os.path.exists(imh_path):
                    img_file = open(imh_path, 'rb+')
                    if img_file:
                        image_base64 = base64.b64encode(img_file.read())
                        if image_base64:
                            values.update({'image':image_base64})
        return super(SlideInherit, self).create(values)
    
    @api.multi
    def write(self, values):
        if values.get('local_url'):
            slide_id = self.env['ir.attachment'].search([('id', '=', int(values.get('local_url')))])
            if slide_id:
                values.update({'slide_type':'video',
                               'mime_type':slide_id.mimetype,
                               })
                imh_path = "/tmp/local_video_v12/video_img_v12.jpg"
                if os.path.exists(imh_path):
                    img_file = open(imh_path, 'rb+')
                    if img_file:
                        image_base64 = base64.b64encode(img_file.read())
                        if image_base64:
                            values.update({'image':image_base64})
        return super(SlideInherit, self).write(values)
    
    def _get_embed_code(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.is_local_url:
                record.embed_code = False
                if record.local_url:
                    if record.local_url.local_url:
                        record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (record.local_url.sudo().local_url,315, 420)
            else:
                if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
                    record.embed_code = '<iframe src="%s/slides/embed/%s?page=1" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (base_url, record.id, 315, 420)
                elif record.slide_type == 'video' and record.document_id:
                    if not record.mime_type:
                        # embed youtube video
                        record.embed_code = '<iframe src="//www.youtube.com/embed/%s?theme=light" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                    else:
                        # embed google doc video
                        record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                else:
                    record.embed_code = False
     
