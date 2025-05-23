import frappe
from frappe.utils import  getdate, nowdate, add_days
@frappe.whitelist()
def get_top_dialer():
	return {
        "value": "faisal",
        "fieldtype": "Text",
    }

	# top_dialer = "Faisal imali"

	# print(f"{top_dialer}  helooo top_dialer \n \n \n \n \n ")

	# return {
    #     "value": top_dialer or "no data",
    #     "fieldtype": "Data",
    # }
