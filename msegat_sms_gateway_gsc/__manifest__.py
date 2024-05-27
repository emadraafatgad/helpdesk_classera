# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Odoo Msegat SMS Gateway || SMS Marketing || SMS Gateway || Bulk SMS || SMS Integration',
    'version': '16.1.0.0',
    'category': 'Tools',
    'license': 'OPL-1',
    
    # Informations
    # Summary: Approx 200 Char (Short description)
    # Description: Long Allowed
    'summary': """
        Odoo Msegat SMS Gateway.
        We also provide Twilio SMS, Sendgrid SMS, MSG91 SMS, Whatsapp SMS,  Zapier SMS, Mailchimp SMS, Skebby, 
        Clicksend SMS, Mobily, Netelip, Whatsapp Integration.
    """,
    'description': """
        Odoo Msegat SMS Gateway helps you integrate & manage Msegat SMS Accounts operations from Odoo. 
        These apps Save your time, Resources, Effort, and Avoid manually manage multiple Msegat SMS Accounts to boost 
        your business SMS Marketing with this connector.
    """,
    
    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com',
    'support': 'growconsultancyservices@gmail.com',
    
    # Application Price Information
    'price': 50,
    'currency': 'EUR',

    # Dependencies
    'depends': ['base', 'mail', 'sale_management', 'stock'],
    
    # Views
    'data': [ 
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/msegat_sms_account_view.xml',
        'views/msegat_sms_groups_view.xml',
        'data/ir_sequence.xml',
        'wizard/msegat_sms_template_preview_views.xml',
        'views/msegat_sms_template_view.xml',
        'views/msegat_sms_send_view.xml',
        'views/msegat_sms_log_history.xml',
        #'views/'
        #'wizard/'
    ],
    
    # Application Main Image    
    'images': ['static/description/app_profile_image.gif'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
