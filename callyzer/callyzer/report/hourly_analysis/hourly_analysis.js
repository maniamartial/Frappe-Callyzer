// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt

frappe.query_reports["Hourly Analysis"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "employee_tag",
			"label": "Employee Tag",
			"fieldtype": "Data",
			
		},
		{
			"fieldname": "employee",
			"label": "Callyzer Employee",
			"fieldtype": "MultiSelectList",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Callyzer Employee", txt);
			}
		},
		{
			"fieldname": "call_type",
			"label": "Call Type",
			"fieldtype": "MultiSelect",
			"options": ["Outgoing", "Missed", "Rejected", "Incoming"]
		}
	]
};
