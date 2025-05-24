import frappe

@frappe.whitelist()
def top_caller():
    latest = frappe.get_list(
        "Callyzer Analysis",
        fields=["top_caller_name", "top_caller_number"],
        order_by="creation desc"
    )
    
    if latest:
        # top_caller = f"{latest[0].top_caller_name} \n {latest[0].top_caller_number}"
        top_caller = f"{latest[0].top_caller_name} \n 1"
        return {
            "value": top_caller,
            "fieldtype": "Data"
        }
    else:
        return {
            "value": "",
            "fieldtype": "Data"
        }