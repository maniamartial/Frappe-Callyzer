// Copyright (c) 2025, Mania and contributors
// For license information, please see license.txt

frappe.query_reports["Callyzer Employee Summary"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "employee",
            "label": "Callyzer Employee",
            "fieldtype": "Link",
            "options": "Employee"
        }
    ]
};
