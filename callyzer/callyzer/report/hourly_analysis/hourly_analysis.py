# Copyright (c) 2025, Mania and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee_tags = filters.get("employee_tag") or []
	employees = filters.get("employee") or []
	call_types = filters.get("call_type") or []

	columns = get_columns()
	conditions = []

	if from_date and to_date:
		conditions.append(f"ha.creation BETWEEN '{from_date}' AND '{to_date}'")

	
	where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

	data = frappe.db.sql(f"""
	SELECT
		ha.hour,
		ha.call_count,
		ha.connected_call_count,
		ha.duration,
		ha.total_calls,
		ha.total_connected_calls,
		ha.total_duration
	FROM `tabHourly Analytics` ha
	{where_clause}
	ORDER BY ha.hour
""", as_dict=1)


	result = []
	for row in data:
		result.append([
			row.hour,
			row.call_count,
			row.connected_call_count,
			row.duration,
			row.total_calls,
			row.total_connected_calls,
			row.total_duration,
			row.employee,
			row.employee_tag,
			row.call_type
		])

	return columns, result

def get_columns():
	return [
		{"label": "Hour", "fieldname": "hour", "fieldtype": "Int", "width": 80},
		{"label": "Call Count", "fieldname": "call_count", "fieldtype": "Int", "width": 100},
		{"label": "Connected Call Count", "fieldname": "connected_call_count", "fieldtype": "Int", "width": 120},
		{"label": "Duration (sec)", "fieldname": "duration", "fieldtype": "Int", "width": 100},
		{"label": "Total Calls", "fieldname": "total_calls", "fieldtype": "Int", "width": 100},
		{"label": "Total Connected Calls", "fieldname": "total_connected_calls", "fieldtype": "Int", "width": 140},
		{"label": "Total Duration (sec)", "fieldname": "total_duration", "fieldtype": "Int", "width": 120},
		{"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"label": "Employee Tag", "fieldname": "employee_tag", "fieldtype": "Link", "options": "Employee Tag", "width": 120},
		{"label": "Call Type", "fieldname": "call_type", "fieldtype": "Data", "width": 100},
	]
