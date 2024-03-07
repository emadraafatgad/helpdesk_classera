# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import qrcode
import base64

# sudo pip3 install rembg
from rembg import remove
import numpy as np
import io
from PIL import Image
#sudo apt install libopencv-dev python3-opencv
import cv2
import numpy as np
from rembg import remove
from PIL import Image, ImageOps, ImageChops, ImageDraw


class HREmployeeVcard(models.Model):
	_name = 'hr.employee.vcard'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']

	name = fields.Char("Name")
	first_name = fields.Char("First Name")
	last_name = fields.Char("Last Name")
	middle_name = fields.Char("Middle Name")
	display_name = fields.Char("Display Name")
	position = fields.Char("Position")
	phone_number = fields.Char("Phone Number")
	local_number = fields.Char("Local Number")
	email = fields.Char("Email")


	employee_id = fields.Many2one('hr.employee', string="Employee")
	birthday = fields.Date("Birthday")
	blood_type	= fields.Char("Blood Type")
	id_number = fields.Char("ID Number")
	date_hired = fields.Date("Date Hired")
	vcard_template = fields.Many2one('hr.employee.vcard.template', string="VCard Template")
	emergency_contact_number = fields.Char("Emergency Contact Number")
	emergency_contact_person = fields.Char("Emergency Contact Person")


	offset = fields.Integer("Offset", default=0)
	qr_code = fields.Binary("QR Code", attachment=False)
	photo = fields.Binary("Photo", attachment=False)
	photo_new = fields.Binary("Photo", attachment=False)
	front_id = fields.Binary("Front ID", attachment=False)
	back_id = fields.Binary("Back ID", attachment=False)

	@api.onchange('last_name', 'first_name', 'middle_name')
	def _compute_name(self):
		for record in self:
			record.name =  f"{record.last_name}, {record.first_name} {record.middle_name}"

	def generate_qr_code(self):
		self.ensure_one()
		#Generate QR Code pointing to url of employee's vcard, convert image to base64 and save to qr_code field
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/vcard/' + str(self.id))
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")

		img_io = io.BytesIO()
		img.save(img_io, 'PNG')
		img_io.seek(0)
		self.qr_code = base64.b64encode(img_io.getvalue())



	def remove_background_and_resize(self):
		self.ensure_one()
		width = 500
		photo_aspect_ratio = 160 / 154  # This is the size of the photo placeholder in the report designer
		photo_placeholder_width = int(width)
		photo_placeholder_height = int(width * photo_aspect_ratio)
		offset_percentage = self.offset / 100

		# Remove background of employee's photo, convert image to base64 and save to photo field
		if self.photo:
			# Create an Image object from BytesIO object
			img = Image.open(io.BytesIO(base64.b64decode(self.photo)))

			# Remove the background
			img_nobg = remove(img)

			# Convert image to grayscale
			gray = cv2.cvtColor(np.array(img_nobg), cv2.COLOR_BGR2GRAY)

			# Load OpenCV face detector
			face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

			# Detect faces
			faces = face_cascade.detectMultiScale(gray, 1.1, 4)

			# Crop the image to the visible part
			bbox = ImageChops.invert(img_nobg).getbbox()
			img_cropped = img_nobg.crop(bbox)

			if len(faces) != 0:
				# Get the bounding box of the first face
				x, y, w, h = faces[0]

				# Measure the width of the space to the left of the face
				width_left = x

				# Calculate the offset to move the image to the left by 10% of the width to the left of the face
				offset_x = int(width_left * offset_percentage)

				# Crop the image from the left side (to the right) with the calculated offset
				img_cropped = img_cropped.crop((offset_x, 0, img_cropped.width, img_cropped.height))

			# Crop the image to remove excess transparent areas
			img_cropped = img_cropped.crop(img_cropped.getbbox())

			# Find the aspect ratio of the image
			img_aspect_ratio = img_cropped.width / img_cropped.height

			# Resize the image to fit the placeholder height while maintaining the aspect ratio
			new_height = photo_placeholder_height
			new_width = new_height * img_aspect_ratio

			# Resize the image to new dimensions
			img_resized = img_cropped.resize((int(new_width), int(new_height)))

			# Create a new blank image with the size of the photo placeholder
			new_image = Image.new("RGBA", (photo_placeholder_width, photo_placeholder_height), (0, 0, 0, 0))

			# Calculate the offset to position the image to the left of the placeholder if the width is wider
			offset_x = 0 if new_width <= photo_placeholder_width else int(new_width - photo_placeholder_width)

			# Paste the resized image onto the new image with the calculated offset
			new_image.paste(img_resized, (-offset_x, 0))

			# Save the output image
			out = io.BytesIO()
			new_image.save(out, format='PNG')
			out.seek(0)

			# Convert the output image to base64
			self.photo_new = base64.b64encode(out.getvalue())

		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}


	
	
	def generate_vcf_content(self):
		vcard = self
		vcf_content = f"""
BEGIN:VCARD
VERSION:3.0
N:{vcard.last_name};{vcard.first_name};{vcard.middle_name}
FN:{vcard.first_name} {vcard.middle_name} {vcard.last_name}
ORG:Your Company
TITLE:{vcard.position}
TEL;TYPE=MOBILE,VOICE:{vcard.phone_number}
TEL;TYPE=WORK,VOICE:{vcard.local_number}
EMAIL;TYPE=PREF,INTERNET:{vcard.email}
END:VCARD
        """
		return vcf_content

		
class HREmployeeVcardTemplate(models.Model):
	_name = 'hr.employee.vcard.template'

	name = fields.Char("Name")
	width = fields.Integer("Width")
	height = fields.Integer("Height")
	offset_y = fields.Integer("Offset Y")
	offset_x = fields.Integer("Offset X")
	front_bg = fields.Binary("Background Image Front", attachment=False)
	back_bg = fields.Binary("Background Image Back", attachment=False)
	vcard_bg = fields.Binary("Background Image VCard", attachment=False)