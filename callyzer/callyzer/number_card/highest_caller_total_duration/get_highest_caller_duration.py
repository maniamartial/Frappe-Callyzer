import frappe

@frappe.whitelist()
def highest_caller_duration():
    latest = frappe.get_list(
        "Callyzer Analysis",
        fields=["highest_total_duration"],
        order_by="creation desc"
    )
    
    if latest:
        highest_caller = f"{latest[0].highest_total_duration} \n 1"
        return {
            "value": highest_caller,
            "fieldtype": "Duration"
        }
    else:
        return {
            "value": 0,
            "fieldtype": "Duration"
        }