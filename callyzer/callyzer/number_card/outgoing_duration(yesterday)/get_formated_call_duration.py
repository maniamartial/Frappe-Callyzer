import frappe
from frappe.utils import format_duration, getdate, nowdate, add_days

@frappe.whitelist()
def get_formated_duration():

    today = getdate(nowdate())

    start_date = add_days(today, -1)
    end_date = start_date
    call_logs = frappe.get_all("Call History Log", filters={"call_type": "Outgoing", "call_date":["between", [start_date, end_date ]]}, fields=["duration"])

    total_duration = sum(log["duration"] for log in call_logs if log["duration"])
    formated_duration = format_duration(total_duration) or 0

    return {
        "value": formated_duration,
        "fieldtype": "Data",
    }