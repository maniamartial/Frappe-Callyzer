# Copyright (c) 2025, Mania and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.utils import get_datetime

import frappe
import json

def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()

	conditions = "1=1"
	params = {}

	if filters.get("company"):
		conditions += " AND company = %(company)s"
		params["company"] = filters.get("company")

	raw_data = frappe.db.sql(f"""
		SELECT
			client_name,
			CONCAT(client_country_code, " ", client_number) AS client,
			total_calls,
			COALESCE(total_incoming_duration, 0) + COALESCE(total_outgoing_duration, 0) AS total_duration,
			total_incoming_calls,
			total_incoming_duration,
			total_outgoing_calls,
			total_outgoing_duration,
			total_missed_calls,
			total_rejected_calls,
			total_connected_calls,
			total_never_attended_calls,
			total_not_picked_by_client,
			last_call_details
		FROM `tabCallyzer Unique Client`
		WHERE {conditions}
		ORDER BY total_calls DESC
	""", params, as_dict=True)

	data = []

	for row in raw_data:
		details = ""
		if row.get("last_call_details"):
			try:
				last_call = json.loads(row["last_call_details"])
				emp_name = last_call.get("emp_name", "")
				emp_number = last_call.get("emp_number", "")
				call_date = last_call.get("call_date", "")
				call_type = last_call.get("call_type", "")
				details = f"{emp_name}\n{emp_number}\n{call_type}"

			except Exception:
				details = "Invalid data"

		row["last_call_details"] = details
		data.append(row)

	return columns, data


def get_columns():
	return [
		{"label": "Client", "fieldname": "client", "fieldtype": "Data", "width": 180},
		{"label": "Total Calls", "fieldname": "total_calls", "fieldtype": "Int", "width": 120},
		{"label": "Total Duration", "fieldname": "total_duration", "fieldtype": "Int", "width": 130},
		{"label": "Incoming Calls", "fieldname": "total_incoming_calls", "fieldtype": "Int", "width": 130},
		{"label": "Incoming Duration", "fieldname": "total_incoming_duration", "fieldtype": "Int", "width": 140},
		{"label": "Outgoing Calls", "fieldname": "total_outgoing_calls", "fieldtype": "Int", "width": 130},
		{"label": "Outgoing Duration", "fieldname": "total_outgoing_duration", "fieldtype": "Int", "width": 140},
		{"label": "Missed", "fieldname": "total_missed_calls", "fieldtype": "Int", "width": 100},
		{"label": "Rejected", "fieldname": "total_rejected_calls", "fieldtype": "Int", "width": 100},
		{"label": "Connected Calls", "fieldname": "total_connected_calls", "fieldtype": "Int", "width": 130},
		{"label": "Never Attended", "fieldname": "total_never_attended_calls", "fieldtype": "Int", "width": 140},
		{"label": "Not Pickup by Client", "fieldname": "total_not_picked_by_client", "fieldtype": "Int", "width": 160},
		{"label": "Last Call Details", "fieldname": "last_call_details", "fieldtype": "Data", "width": 160},
	]
