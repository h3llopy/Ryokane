# -*- coding: utf-8 -*-
###############################################################################
#
#   mail_message_bubbles for Odoo
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

{
    'name': 'eLearning Local Video',
    'version': '12.0.1',
    'description': """Geminate comes with a handy feature to upload any local video on eLearning slides instead of online video url of youtube, google drive or anyother 3rd party cloud public url. 
                        So no need of any 3rd party websites intervention on your inhouse eLearning plateform.""",
    'author': 'Geminate Consultancy Services',
    'company': 'Geminate Consultancy Services',
    'website': 'https://www.geminatecs.com/',
    'summary': """Website Slides Local Video.""",
    'category': 'eLearning',
    'data': [
            'security/ir.model.access.csv',
            'data/scheduler_date.xml',
            'views/slide_slide_view.xml',
            'views/website_slides_templates_lesson_fullscreen.xml',
    ],
    'depends': ['website_slides'],
    "license": "Other proprietary",
    'qweb' : [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/icon.png'],
    "price": 24.99,
    "currency": "EUR"
}
