// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt

frappe.query_reports["Callyzer Call History"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options: "Company"
		},
		{
			fieldname: "employee",
			label: "Employee",
			fieldtype: "Data"
		}
	],
	"no_total_row": 1,

	formatter: function (value, row, column, data, default_formatter) {
	value = default_formatter(value, row, column, data);

	if (column.fieldname === "call_type" && data) {
		if (data.call_type === "Outgoing") {
			value = `<span style="color: orange;">${value}</span>`;
		}else if(data.call_type=="Incoming"){
			value = `<span style="color: green;">${value}</span>`;
		}
	}

	return value;
}
}
