import frappe
@frappe.whitelist()
def top_answered():
    latest = frappe.get_list(
        "Callyzer Analysis",
        fields=["top_answered_name", "top_answered_number"],
        order_by="creation desc"
    )
    
    if latest:
        # top_answered = f"{latest[0].top_answered_name} \n {latest[0].top_answered_number}"
        top_answered = top_caller = f"{latest[0].top_answered_name} \n 1"
        return {
            "value": top_answered,
            "fieldtype": "Data"
        }
    else:
        return {
            "value": "",
            "fieldtype": "Data"
        }