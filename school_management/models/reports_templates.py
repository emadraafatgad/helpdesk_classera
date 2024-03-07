from odoo import models, fields, api, _
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from markupsafe import Markup
import re

class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class ReportTemplate(models.Model):
    _name = 'general.report.template'

    name = fields.Char(required=True)
    content = fields.Html(string="Content")
    test_content = fields.Html()
    model_name_id = fields.Many2one('ir.model')
    field_fields_ids = fields.Many2many('ir.model.fields',domain="[('model_id','=',model_name_id)]")
    rec_model = fields.Many2one('res.partner')
    rec_id=  fields.Many2one('res.partner')

    def create_variable_dic(self):
        vardic ={}
        for field_val in self.field_fields_ids:
            if field_val.name not in vardic:
                try:
                    vardic[field_val.name] = self.rec_id[field_val.name] if field_val.ttype not in ['many2many','many2one','one2many'] else '-'
                except :
                    continue
        return vardic
    def compute_test_content(self):
        input_string = self.content

        # Dictionary containing variable names and their corresponding values
        variables = self.create_variable_dic()
        print('variables')
        print(variables)
        # Define a regular expression pattern to match strings between ##
        pattern = r'##(.*?)##'

        # Function to replace the matched substrings with variable values
        def replace_string(match):
            variable_name = match.group(1)
            print('variable_name')
            print(variable_name)
            if variable_name in variables:
                print(variables[variable_name])
                return variables[variable_name]
            print(match)
            return match.group(0)  # If variable not found, return the original match

        # Use re.sub() to replace the matched substrings based on variable values
        result = re.sub(pattern, replace_string, input_string)

        # Print the updated string after replacement
        print(result)
        self.test_content = result


    @api.onchange('model_name_id')
    def onchange_some_condition_field(self):
        if self.model_name_id:
            # self.rec_model = fields.Many2one(self.model_name_id.model)
            self.rec_model = fields.Many2one('academic.year')
            print(self.rec_model)
        # Add more conditions as needed
        else:
            self.rec_model = fields.Many2one('res.partner')  # Default back to model.b


    @api.onchange('model_name_id')
    def get_general_fields(self):
        if self.model_name_id:
            fieldat=  self.env['ir.model.fields'].search([('model_id','=',self.model_name_id.id)])
            self.field_fields_ids = [(5,0,0)]
            self.field_fields_ids = [(6,0,fieldat.ids)]

class ContentTemplateReport(models.Model):
    _name = 'content.template.report'

    template_report = fields.Many2one('general.report.template')
    content = fields.Html(string="Content")

    @api.onchange('template_report')
    def get_content_template_date(self):
        if self.template_report:
            content = self.template_report.content if self.template_report.content else ""
            # print(type(content))
            content = content.replace("##note", self.note if "##note" in content else "")
            content = content.replace("##date", str(self.date_order) if "##date" in content else "")
            content = content.replace("##ref", self.name if "##ref" in content else "")
            content = content.replace("##client", self.partner_id.name if "##client" in content else "")
            content = content.replace("##terms_and_conndition", self.note if "##terms_and_conndition" in content else "")
            order = self.order_line_table()
            # soup = bs4(order)
            # print(order)
            # print(soup.get_text())
            index = content.find("##order")
            # print(index,type(index))
            content = content.replace(Markup("<p>##order</p>"), Markup(order))
            # content = content.replace("##order", order)
            # print(content)
            order = Markup(order)
            # content= content[:index-3] + order + content[index +12:]
            # print(content)
            self.content = content

    def order_line_table(self):
        color = "#FFFF00"
        order_lines = self.order_line
        # dir="rtl"
        table = """"""
        table = """
        <table class='table table-bordered'>
              <tbody>
                <tr>
                  <td style='background: {};' >Number</td>
                  <td style='background: {}; '>Our Offer DESCREPTION</td>
                  <td style='background: {}; '>QTY</td>
                  <td style='background: {}; '>Unit</td>
                  <td style='background: {}; '>Up $</td>
                  <td style='background: {}; '>TP $</td>
                </tr>
                        """.format(color, color, color, color, color, color)
        counter = 1
        for line in order_lines:
            table += """
            <tr >
            <td >{}</td>
            <td >{}</td>
            <td >{}</td>
            <td >{}</td>
            <td >{}</td>
            <td >{}</td>
            </tr>
            """.format(counter, line.name, line.product_uom_qty, line.product_uom.name, line.price_unit,
                       line.price_subtotal)
            counter += 1
        table += """
        <tr >
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td style="background: {}; ">{}</td>
            <td >{}</td>
        </tr>""".format(color, _('Total'), str(self.amount_total))
        table += """  </tbody>
            </table>
            """
        # print(table)
        return table
