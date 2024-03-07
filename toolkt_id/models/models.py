# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class ToolkitIdSheet(models.Model):
	_name = 'tookit.id.sheet'

	user_id = fields.Many2one('res.users','User ID',  track_visibility='onchange', default=lambda self: self.env.user.id)
	active = fields.Boolean(string='Active', default=True)
	#Front
	firstname = fields.Char(string='First Name', required=True)
	lastname = fields.Char(string='Last Name', required=True)
	middlename = fields.Char(string='Middle Name')
	suffix = fields.Selection([('Jr','Jr'),
							('Sr','Sr'),
							('I','I'),
							('II','II'),
							('III','III'),
							('IV','IV')],
							string='Suffix')
	position = fields.Char(string='Position')
	id_number = fields.Char(string='ID Number')
	#Back
	email = fields.Char(string='Email Address')
	mobile_number = fields.Char(string='Mobile Number', required=True)
	tin = fields.Char(string='TIN Number')
	address = fields.Char(string='Address', required=True)
	date_of_birth = fields.Date(string='Date of Birth', required=True)
	gender = fields.Selection([('M','Male'),
							('F','Female'),
							('O','Others')],
							string='Gender')
	blood_type = fields.Selection([('A','A'),
							('B','B'),
							('AB','AB'),
							('O','0')],
							string='Blood Type')
	#Emergency Contact Person
	ecp_name = fields.Char(string='Contact Person', required=True)
	contact_number = fields.Char(string='Contact Number', required=True)
	relation = fields.Char(string='Relation', required=True)
	#Extras
	image = fields.Binary(string='Employee Profile', attachment=False)
	signature = fields.Binary(string='Signature', attachment=False)
	employee_image = fields.Image(string='Profile', attachment=False)
	