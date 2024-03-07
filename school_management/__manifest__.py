# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'School Management',
    'version': '1.2',
    'summary': 'Classera School Management',
    'sequence': 10,
    'author': "Emad Raafat",
    'description': """
Invoicing & Payments
====================
The specific and easy-to-use Invoicing system in C-smart allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Learning',
    'website': 'https://www.classera.com',
    'depends': ['base_setup', 'product', 'account', 'multi_branch_base', 'report_xlsx'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/academic_year.xml',
        'views/reports_templates.xml',
        'views/stage.xml',
        'views/level.xml',
        'views/student_sequence.xml',
        'views/school_class.xml',
        'views/subjects.xml',
        'views/installments.xml',
        'views/fees_plan.xml',
        'views/product_template.xml',
        'views/fees_structure.xml',
        'views/discount.xml',
        'views/discount_template.xml',
        'views/student.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/product_pricelist.xml',
        'views/advance_payment.xml',
        'wizard/payment_collection_wiz.xml',
        'wizard/payment_collection_pdf.xml',
        'wizard/student_collection_report.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'license': 'LGPL-3',
}
