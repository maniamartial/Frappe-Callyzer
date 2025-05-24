// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt

frappe.query_reports["Unique Clients"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options: "Company",
			reqd: 1
		}
	]
};
