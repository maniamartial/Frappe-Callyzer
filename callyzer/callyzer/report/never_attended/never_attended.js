// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt
frappe.query_reports["Never Attended"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Callyzer Employee",
			"width": "120"
		},
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		}
	],
formatter: function (value, row, column, data, default_formatter) {
	value = default_formatter(value, row, column, data);

	if (column.fieldname === "call_type" && data) {
		if (data.call_type === "Missed") {
			value = `<span style="color: #FF0000;">${value}</span>`;
		} else if (data.call_type === "Rejected") {
			value = `<span style="color: #cc6666;">${value}</span>`;
		}
	}

	return value;
}

};
