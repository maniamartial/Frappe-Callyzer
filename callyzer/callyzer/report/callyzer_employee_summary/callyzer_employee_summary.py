# # Copyright (c) 2025, Mania and contributors
# # For license information, please see license.txt

# # import frappe

# import frappe
# from datetime import datetime

# def execute(filters=None):
# 	filters = frappe._dict(filters or {})

# 	columns = get_columns()
# 	hour_slots = get_hour_slots()

# 	# Prepare SQL conditions
# 	conditions = ["1=1"]
# 	if filters.get("employee"):
# 		conditions.append("employee = %(employee)s")
# 	# if filters.get("from_date") and filters.get("to_date"):
# 	#     conditions.append("call_date BETWEEN %(from_date)s AND %(to_date)s")

# 	where_clause = " AND ".join(conditions)

# 	data = frappe.db.sql(f"""
# 		SELECT * FROM `tabCallyzer Employee Summary`
# 		WHERE {where_clause}
# 	""", filters, as_dict=True)
# 	employee_data = {}
# 	for row in data:
# 		emp = row["employee"]
# 		hour = row.get("hour")

# 		if not hour:
# 			continue  # Skip rows with missing hour slot to avoid KeyError

# 		if emp not in employee_data:
# 			employee_data[emp] = initialize_employee_record(emp, hour_slots)

# 		update_totals(employee_data[emp], row, hour, hour_slots)

# 	# Format durations into time strings
# 	for record in employee_data.values():
# 		record["total_duration"] = seconds_to_time(record["total_duration"])
# 		for h, _ in hour_slots:
# 			record[f"duration_{h}"] = seconds_to_time(record[f"duration_{h}"])

# 	return columns, list(employee_data.values())

# def get_columns():
# 	columns = [
# 		{"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 180},
# 		{"label": "Total Calls", "fieldname": "total_calls", "fieldtype": "Int", "width": 100},
# 		{"label": "Total Connected Calls", "fieldname": "total_connected_calls", "fieldtype": "Int", "width": 140},
# 		{"label": "Total Duration", "fieldname": "total_duration", "fieldtype": "Time", "width": 120},
# 	]

# 	for hour, label in get_hour_slots():
# 		columns.extend([
# 			{"label": f"{label} - Calls", "fieldname": f"calls_{hour}", "fieldtype": "Int", "width": 90},
# 			{"label": f"{label} - Connected", "fieldname": f"connected_{hour}", "fieldtype": "Int", "width": 100},
# 			{"label": f"{label} - Duration", "fieldname": f"duration_{hour}", "fieldtype": "Time", "width": 110},
# 		])
# 	return columns

# def get_hour_slots():
# 	return [
# 		("before_10", "Before 10:00 AM"),
# 		("10", "10:00 AM - 10:59 AM"),
# 		("11", "11:00 AM - 11:59 AM"),
# 		("12", "12:00 PM - 12:59 PM"),
# 		("13", "01:00 PM - 01:59 PM"),
# 		("14", "02:00 PM - 02:59 PM"),
# 		("15", "03:00 PM - 03:59 PM"),
# 		("16", "04:00 PM - 04:59 PM"),
# 		("17", "05:00 PM - 05:59 PM"),
# 		("18", "06:00 PM - 06:59 PM"),
# 		("19", "07:00 PM - 07:59 PM"),
# 	]

# def initialize_employee_record(employee, hour_slots):
# 	record = {
# 		"employee": employee,
# 		"total_calls": 0,
# 		"total_connected_calls": 0,
# 		"total_duration": 0,
# 	}
# 	for h, _ in hour_slots:
# 		record[f"calls_{h}"] = 0
# 		record[f"connected_{h}"] = 0
# 		record[f"duration_{h}"] = 0
# 	return record

# def update_totals(record, row, hour, hour_slots):
# 	record["total_calls"] += row.get("total_calls", 0)
# 	record["total_connected_calls"] += row.get("total_connected_calls", 0)
# 	duration_sec = time_to_seconds(row.get("total_duration"))
# 	record["total_duration"] += duration_sec

# 	if hour not in dict(hour_slots):
# 		return  # Ignore unexpected hour values

# 	record[f"calls_{hour}"] += row.get("total_calls", 0)
# 	record[f"connected_{hour}"] += row.get("total_connected_calls", 0)
# 	record[f"duration_{hour}"] += duration_sec

# def time_to_seconds(t):
# 	if not t:
# 		return 0
# 	if isinstance(t, str):
# 		parts = t.split(":")
# 		if len(parts) == 3:
# 			h, m, s = map(int, parts)
# 		elif len(parts) == 2:
# 			h, m = map(int, parts)
# 			s = 0
# 		else:
# 			return 0
# 		return h * 3600 + m * 60 + s
# 	return int(t)

# def seconds_to_time(seconds):
# 	h = seconds // 3600
# 	m = (seconds % 3600) // 60
# 	s = seconds % 60
# 	return f"{h:02}:{m:02}:{s:02}"

# Copyright (c) 2025, Mania and contributors
# For license information, please see license.txt

import frappe
from datetime import timedelta

def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns()

	# Prepare SQL conditions
	conditions = ["1=1"]
	if filters.get("employee"):
		conditions.append("employee = %(employee)s")

	where_clause = " AND ".join(conditions)

	data = frappe.db.sql(f"""
		SELECT 
			employee,
			employee_name,
			SUM(total_calls) AS total_calls,
			SUM(total_connected_calls) AS total_connected_calls,
			SUM(total_duration) AS total_duration
		FROM `tabCallyzer Employee Summary`
		WHERE {where_clause}
		GROUP BY employee
	""", filters, as_dict=True)

	# Convert duration (in seconds) to timedelta object
	for row in data:
		duration_seconds = row.get("total_duration") or 0  # If None, use 0
		row["total_duration"] = seconds_to_timedelta(duration_seconds)

	return columns, data

def get_columns():
	return [
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
		{"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Callyzer Employee", "width": 180},
		{"label": "Total Calls", "fieldname": "total_calls", "fieldtype": "Int", "width": 100},
		{"label": "Total Connected Calls", "fieldname": "total_connected_calls", "fieldtype": "Int", "width": 140},
		{"label": "Total Duration", "fieldname": "total_duration", "fieldtype": "Duration", "width": 120},
	]


def seconds_to_timedelta(seconds):
	return timedelta(seconds=int(seconds))
