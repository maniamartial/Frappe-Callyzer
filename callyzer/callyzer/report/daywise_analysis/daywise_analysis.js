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
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Apply color to columns
		if (column.fieldname) {
			if (column.fieldname.includes("connected")) {
				value = `<span style="color: blue;">${value}</span>`;
			} else if (column.fieldname.includes("calls")) {
				value = `<span style="color: green;">${value}</span>`;
			} else if (column.fieldname.includes("duration")) {
				value = `<span style="color: goldenrod;">${value}</span>`;
			}
		}

		return value;
	}
};

