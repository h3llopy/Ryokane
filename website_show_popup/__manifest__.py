# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################

{
    "name": "Website Show Popup (Website Popup)",
    "summary": "This module helps you to Show Popup Message while load odoo website pages",
    "version": "12.0.1",
    "description": """This module helps you to Show Popup Message while load odoo website pages""",    
    "author": "Ananthu Krishna",
    "maintainer": "Ananthu Krishna",
    "license" :  "Other proprietary",
    "website": "http://www.codersfort.com",
    "images": ["images/website_show_popup.png"],
    "category": "Website",
    "depends": ["website"],
    "data": [
        'views/assets.xml',
        'views/website_views.xml',
        'views/website_templates.xml',
    ],    
    "installable": True,
    "application": True,
    "price"                :  15,
    "currency"             :  "EUR",
    "pre_init_hook"        :  "pre_init_check",   
}
