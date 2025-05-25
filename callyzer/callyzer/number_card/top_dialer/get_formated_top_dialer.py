import frappe

@frappe.whitelist()
def get_top_dialer():
    latest = frappe.get_list(
        "Callyzer Analysis",
        fields=["top_dialer_name", "top_dialer_number"],
        order_by="creation desc",
        limit_page_length=1
    )
    
    if latest:
        # top_dialer = f"{latest[0].top_dialer_name} \n {latest[0].top_dialer_number}"
        top_dialer = f"{latest[0].top_dialer_name} \n 1"
        return {
            "value": top_dialer,
            "fieldtype": "Data"
        }
    else:
        return {
            "value": "",
            "fieldtype": "Data"
        }
        