from odoo import http
from odoo.http import request, content_disposition, route

class VCardController(http.Controller):

    @http.route('/vcard/<int:vcard_id>', type='http', auth='public', website=True)
    def vcard_profile(self, vcard_id, **kwargs):
        vcard = request.env['hr.employee.vcard'].sudo().browse(vcard_id)
        return request.render('hr_vcard.vcard_template', {'vcard': vcard})


    @route('/vcard/download/<int:vcard_id>', type='http', auth='public')
    def download_vcard(self, vcard_id, **kw):
        # Search for the vcard with the given ID
        vcard = request.env['hr.employee.vcard'].sudo().browse(vcard_id)
        
        if not vcard:
            return request.not_found()
        
        vcf_content = vcard.generate_vcf_content()  # a method that generates VCF content from vcard data
        file_name = '%s.vcf' % vcard.name  # Create file name
        headers = [
            ('Content-Type', 'text/x-vcard'),
            ('Content-Disposition', content_disposition(file_name)),
        ]
        return request.make_response(vcf_content, headers)