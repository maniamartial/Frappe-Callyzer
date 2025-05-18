

import frappe
from datetime import datetime
from frappe import _
import json

def get_callyzer_settings(company):
    settings = frappe.get_all("Callyzer Settings", filters={"is_active": 1, "company":company}, fields=["name", "domain_api", "api_key", "company", "call_log"])
    return settings[0] if settings else None


def normalize_payload(payload):
    """Normalize input payload to a list of data dictionaries."""
    if isinstance(payload, list):
        return payload
    elif isinstance(payload, dict):
        return payload.get("result", []) or [payload]
    else:
        frappe.throw(_("Unexpected payload format"))

def get_employees():
    employees_id = []
    all_callyzer_employee = frappe.get_all("Callyzer Employee", fields=["name"])
    for employee in all_callyzer_employee:
        employees_id.append(employee.name)
    return employees_id

def format_time_timestamp_(date):
    return int(datetime.timestamp(date))
