# -*- coding: utf-8 -*-
{
    'name': "HR VCard",

    'summary': """
        HR Virtual Business Card""",

    'description': """
        Long description of module's purpose
    """,

    'author': "TOOLKIT INC",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'hr',
        'tk_pentaho_reports_odoo',
    ],

    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/employee_vcard.xml',
        'views/vcard_template.xml',
        'reports/reports.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'hr_vcard/static/src/scss/vcard_template.scss',
        ],
    },

    # only loaded in demonstration mode
    'demo': [
    ],
}
