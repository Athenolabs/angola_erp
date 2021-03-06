# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model import no_value_fields
from frappe.translate import set_default_language
from frappe.utils import cint
from frappe.utils.momentjs import get_all_timezones
#from frappe.twofactor import toggle_two_factor_auth
from angola_erp.util.twofactor import toggle_two_factor_auth


def validate(doc, method):
	print 'SYSTEM SETTINGS - VALIDATE'
	print 'SYSTEM SETTINGS - VALIDATE'
	print 'SYSTEM SETTINGS - VALIDATE'

	enable_password_policy = cint(doc.enable_password_policy) and True or False
	minimum_password_score = cint(doc.minimum_password_score) or 0
	if enable_password_policy and minimum_password_score <= 0:
		frappe.throw(_("Please select Minimum Password Score"))
	elif not enable_password_policy:
		doc.minimum_password_score = ""

	for key in ("session_expiry", "session_expiry_mobile"):
		if doc.get(key):
			parts = doc.get(key).split(":")
			if len(parts)!=2 or not (cint(parts[0]) or cint(parts[1])):
				frappe.throw(_("Session Expiry must be in format {0}").format("hh:mm"))

	if doc.enable_two_factor_auth:
		if doc.two_factor_method=='SMS':
			print 'enable two factor SMS'
			if not frappe.db.get_value('SMS Settings', None, 'sms_gateway_url'):
				frappe.throw(_('Please setup SMS before setting it as an authentication method, via SMS Settings'))
		toggle_two_factor_auth(True, roles=['All'])

def on_update(doc):
	for df in doc.meta.get("fields"):
		if df.fieldtype not in no_value_fields:
			frappe.db.set_default(df.fieldname, doc.get(df.fieldname))

	if doc.language:
		set_default_language(doc.language)

	frappe.cache().delete_value('system_settings')
	frappe.cache().delete_value('time_zone')
	frappe.local.system_settings = {}

@frappe.whitelist()
def load():
	if not "System Manager" in frappe.get_roles():
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	all_defaults = frappe.db.get_defaults()
	defaults = {}

	for df in frappe.get_meta("System Settings").get("fields"):
		if df.fieldtype in ("Select", "Data"):
			defaults[df.fieldname] = all_defaults.get(df.fieldname)

	return {
		"timezones": get_all_timezones(),
		"defaults": defaults
	}
