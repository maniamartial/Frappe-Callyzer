import frappe
def convert_sec(seconds):
	hours = seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60

	return f"{hours} hr {minutes} min {seconds} sec"

@frappe.whitelist()
def get_formated_duration():
    call_logs = frappe.get_all("Callyzer Attendance call", filter={"call_type": "Incoming"}, fields=["duration"])

    total_duration = sum(log["duration"] for log in call_logs if log["duration"])
    formated_duration = convert_sec(total_duration)

    return {
        "value": formated_duration,
        "fieldtype": "Data",
    }
