# Copyright (c) 2025, Mania and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.utils import getdate

def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()

	conditions = ["call_status = 'Missed'", "call_type = 'Outgoing'"]

	if filters.get("employee"):
		conditions.append("employee = %(employee)s")
	if filters.get("from_date"):
		conditions.append("call_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("call_date <= %(to_date)s")

	where_clause = " AND ".join(conditions)

	data = frappe.db.sql(f"""
		SELECT
			employee,
   			emp_name,
			client_number AS to_number,
			call_type,
			call_date,
			call_time
		FROM `tabCallyzer Attendance Call`
		WHERE {where_clause}
		ORDER BY call_date DESC, call_time DESC
	""", filters, as_dict=True)

	return columns, data

def get_columns():
	return [
		{"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 160},
  		{"label": "Employee Name", "fieldname": "emp_name", "fieldtype": "Data", "width": 160},

		{"label": "To Number", "fieldname": "to_number", "fieldtype": "Data", "width": 150},
		{"label": "Call Type", "fieldname": "call_type", "fieldtype": "Data", "width": 120},
		{"label": "Date", "fieldname": "call_date", "fieldtype": "Date", "width": 120},
		{"label": "Time", "fieldname": "call_time", "fieldtype": "Data", "width": 100},
	]
