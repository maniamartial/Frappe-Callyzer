import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_formated_duration():
    today = datetime.today().date()
    start_date = today - timedelta(days=1)
    end_date = start_date

    call_logs = frappe.get_all("Call History Log", filters={"call_type": "Outgoing", "call_date":["between", [start_date, end_date ]]}, fields=["duration"])
    total_duration = sum(log["duration"] for log in call_logs if log["duration"])

    return {
        "value": total_duration,
        "fieldtype": "Duration",
    }