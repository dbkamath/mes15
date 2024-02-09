# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Import Employee Expenses From Excel",
    "version" : "17.0.0.0",
    "category" : "Human Resources",
    'summary': 'Apps for Import HR Expense Import Expense Import Expense sheet Import Expenses import HR expenses import human resources expense from excel import expense from excel import expense from xls import employee expense import mass expense import',
    "description": """  Import Employee Expense,
                        import employee expense from excel, 
                        import employee expense from xls,
                        import employee expense from csv,
                        import employee expense from by product,
                        import employee expense with data,
                        import employee expense in odoo,   """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "price": 10,
    'license': 'OPL-1',
    "currency": 'EUR',
    "depends" : ['base','hr_expense','sale_management'],
    "data": [
            'views/expense_import_wizard_view.xml',
            'security/ir.model.access.csv',
            'security/security.xml',
            'data/attachment_sample.xml',
        ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/UOkHrkrxIgw',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
