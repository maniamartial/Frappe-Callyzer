// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt
frappe.query_reports["Daywise Analysis"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7)
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "chart_type",
			label: "Chart Type",
			fieldtype: "Select",
			options: ["Bar", "Line"],
			default: "Bar"
		}
	]
};
