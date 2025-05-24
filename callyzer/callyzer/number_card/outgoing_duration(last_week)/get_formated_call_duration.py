import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_formated_duration():
    today = datetime.today().date()

    curr_week_start = today - timedelta(days=today.weekday())
    prev_week_start = curr_week_start - timedelta(days=7)
    prev_week_end = prev_week_start + timedelta(days=6)
    
    call_logs = frappe.get_all("Call History Log", filters={"call_type": "Outgoing", "call_type": "Incoming", "call_date":["between", [prev_week_start, prev_week_end]]}, fields=["duration"])
    total_duration = sum(log["duration"] for log in call_logs if log["duration"])
    return {
        "value": total_duration,
        "fieldtype": "Duration",
    }