# -*- coding: utf-8 -*-
def print_report(self, cr, uid, ids, context=None): 
        return {
            'type': 'ir.actions.report',
            'report_name': 'tookit.id.sheet',
            'nodestroy' : True
        }