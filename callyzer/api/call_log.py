import frappe
import requests
import json
from callyzer.callyzer.utils import get_callyzer_settings, normalize_payload, get_employees, format_time_timestamp_
from callyzer.api.fetch_employee import parse_datetime, process_employee
from frappe import _
from datetime import datetime

#Tested working
@frappe.whitelist()
def fetch_summary_report():
    call_from = format_time_timestamp_(datetime.strptime(frappe.form_dict.get("start_date"), "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(frappe.form_dict.get("end_date"), "%Y-%m-%d %H:%M:%S"))
    company = frappe.form_dict.get("company")

    settings = get_callyzer_settings(company)
 
    url = f"{settings.domain_api}/call-log/summary"
    token = settings.api_key

    employee_ids = get_employees()
    
    payload = {
        "call_from": int(call_from),
        "call_to": int(call_to),
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "emp_numbers": employee_ids,
        "duration_les_than": 200,
        "emp_tags": ["api"],
        "is_exclude_numbers": True
    }
    results = post_api(url, token, payload)
    process_total_summary_calls(results, company)
    return results

def process_total_summary_calls(result, company):
    """
    Insert a new Callyzer Total Summary document from API response.
    
    :param data: Dictionary with 'result' from Callyzer API.
    :param company: Optional. Link to Company.
    :param employee: Optional. Link to Employee.
    :param for_date: Optional. Date of the summary (default: today).
    """
    
    doc = frappe.new_doc("Callyzer Total Summary")
    
    doc.total_incoming_calls = result.get("total_incoming_calls", 0)
    doc.total_incoming_duration = result.get("total_incoming_duration", 0)
    doc.total_outgoing_calls = result.get("total_outgoing_calls", 0)
    doc.total_outgoing_duration = result.get("total_outgoing_duration", 0)
    doc.total_missed_calls = result.get("total_missed_calls", 0)
    doc.total_rejected_calls = result.get("total_rejected_calls", 0)
    doc.total_calls = result.get("total_calls", 0)
    doc.total_duration = result.get("total_duration", 0)
    doc.total_never_attended_calls = result.get("total_never_attended_calls", 0)
    doc.total_not_pickup_by_clients_calls = result.get("total_not_pickup_by_clients_calls", 0)
    doc.total_unique_clients = result.get("total_unique_clients", 0)
    doc.total_working_hours = result.get("total_working_hours", "00:00:00")
    doc.total_connected_calls = result.get("total_connected_calls", 0)
    doc.company = company
    doc.insert(ignore_permissions=True)
    return doc.name
    
def process_call_logs(employee_name, call_logs):
    """Create new call logs for the employee and return the number created."""
    count = 0
    for call in call_logs:
        if frappe.db.exists("Callyzer Call Log", {"external_id": call["id"]}):
            continue

        doc = frappe.new_doc("Callyzer Call Log")
        doc.employee = employee_name
        doc.call_log_id = call["id"]
        doc.client_name = call["client_name"]
        doc.client_country_code = call["client_country_code"]
        doc.client_no = call["client_number"]
        doc.duration = call["duration"]
        doc.call_type = call["call_type"]
        doc.call_date = call["call_date"]
        doc.call_time = call["call_time"]
        doc.note = json.dumps(call.get("note", ""))
        doc.call_recording_url = call["call_recording_url"]
        doc.crm_status = call.get("crm_status")
        doc.reminder_date = call.get("reminder_date")
        doc.reminder_time = call.get("reminder_time")
        doc.synced_at = parse_datetime(call.get("synced_at"))
        doc.modified_at = parse_datetime(call.get("modified_at"))

        doc.insert(ignore_permissions=True)
        count += 1

    return count

#Tested working
@frappe.whitelist()
def fetch_employee_summary_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)

    url = f"{settings.domain_api}/call-log/employee-summary"

    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "emp_numbers": [],
        "duration_les_than": 20,
        "emp_tags": [],
        "is_exclude_numbers": True
    }
    result = post_api(url, settings.api_key, payload)
    handle_employee_summary_response(result, company)
    return {"status": "success", "message": "Employee summary report fetched successfully"}
   
#Tested working
def handle_employee_summary_response(result, company):
    for emp in result:
        if not frappe.db.exists("Callyzer Employee", {"employee_no": emp.get("emp_number")}):
            process_employee(emp)

        doc = frappe.new_doc("Callyzer Employee Summary")
        doc.employee_name = emp.get("emp_name")
        doc.employee_code = emp.get("emp_code")
        doc.emp_country_code = emp.get("emp_country_code")
        doc.employee = emp.get("emp_number")
        doc.emp_tags = ", ".join(emp.get("emp_tags", []))
        doc.total_incoming_calls = emp.get("total_incoming_calls")
        doc.total_outgoing_calls = emp.get("total_outgoing_calls")
        doc.total_missed_calls = emp.get("total_missed_calls")
        doc.total_rejected_calls = emp.get("total_rejected_calls")
        doc.total_calls = emp.get("total_calls")
        doc.total_duration = emp.get("total_duration")
        doc.total_connected_calls = emp.get("total_connected_calls")
        doc.total_never_attended_calls = emp.get("total_never_attended_calls")
        doc.total_not_pickup_by_clients_calls = emp.get("total_not_pickup_by_clients_calls")
        doc.total_unique_clients = emp.get("total_unique_clients")
        doc.total_working_hours = emp.get("total_working_hours")
        doc.avg_duration_per_call = emp.get("avg_duration_per_call")
        doc.avg_incoming_duration = emp.get("avg_incoming_duration")
        doc.avg_outgoing_duration = emp.get("avg_outgoing_duration")

        doc.last_call_log = json.dumps(emp.get("last_call_log", {}))

        doc.insert(ignore_permissions=True)
        inserted += 1

    return {"status": "success", "inserted": inserted}

#Fetch analysis report
@frappe.whitelist()
def fetch_analysis_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")
    
    call_from = int(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").timestamp())
    call_to = int(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").timestamp())

    settings = get_callyzer_settings(company)
 
    url = f"{settings.domain_api}/call-log/analysis"

    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "is_exclude_numbers": True
    }
    result = post_api(url, settings.api_key, payload)
    handle_analysis_report(start_date, end_date, company, result)
    return {"status": "success", "message": "Analysis report fetched successfully"}


def handle_analysis_report(start_date, end_date, company, result):
    doc = frappe.new_doc("Callyzer Analysis")
    doc.start_date = start_date
    doc.end_date = end_date
    doc.company = company

    # Average Duration
    avg = result.get("average_duration", {})
    doc.total_duration = avg.get("total_duration")
    doc.avg_per_call = avg.get("per_call")
    doc.total_calls = avg.get("total_calls")
    doc.avg_per_day = avg.get("per_day")
    doc.total_days = avg.get("total_days")
    doc.avg_per_incoming = avg.get("per_incoming_call")
    doc.total_incoming_calls = avg.get("total_incoming_calls")
    doc.avg_per_outgoing = avg.get("per_outgoing_call")
    doc.total_outgoing_calls = avg.get("total_outgoing_calls")

    # Top Dialer
    dialer = result.get("top_dialer", {})
    doc.top_dialer_name = dialer.get("emp_name")
    doc.top_dialer_number = dialer.get("emp_number")
    doc.top_dialer_tags = ", ".join(dialer.get("emp_tags", []))
    doc.top_dialer_outgoing_calls = dialer.get("total_outgoing_calls")

    # Top Answered
    answered = result.get("top_answered", {})
    doc.top_answered_name = answered.get("emp_name")
    doc.top_answered_number = answered.get("emp_number")
    doc.top_answered_tags = ", ".join(answered.get("emp_tags", []))
    doc.top_answered_incoming_calls = answered.get("total_incoming_calls")

    # Top Caller
    caller = result.get("top_caller", {})
    doc.top_caller_name = caller.get("emp_name")
    doc.top_caller_number = caller.get("emp_number")
    doc.top_caller_tags = ", ".join(caller.get("emp_tags", []))
    doc.top_caller_total_calls = caller.get("total_calls")

    # Longest Duration
    long_dur = result.get("longest_duration", {})
    doc.longest_duration_name = long_dur.get("emp_name")
    doc.longest_duration_number = long_dur.get("emp_number")
    doc.longest_duration_tags = ", ".join(long_dur.get("emp_tags", []))
    doc.longest_call_duration = long_dur.get("duration")

    # Highest Duration
    high_dur = result.get("highest_total_duration", {})
    doc.highest_duration_name = high_dur.get("emp_name")
    doc.highest_duration_number = high_dur.get("emp_number")
    doc.highest_duration_tags = ", ".join(high_dur.get("emp_tags", []))
    doc.highest_total_duration = high_dur.get("total_duration")

    doc.insert(ignore_permissions=True)
    return {"status": "success", "message": "Analysis data inserted"}

        
#Fetch Never Attended Report
@frappe.whitelist()
def fetch_never_attended_calls():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)
 
    url = f"{settings.domain_api}/call-log/never-attended"
  
    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "emp_numbers": [],
        "emp_tags": [],
        "is_exclude_numbers": True,
        "page_no": 1,
        "page_size": 10
    }
    result = post_api(url, settings.api_key, payload)
    handle_never_attended_calls(result)

    return {"status": "success", "message": "Analysis data inserted"}

def handle_never_attended_calls(response):
    for emp in response:
        emp_number = emp.get("emp_number")

        if not frappe.db.exists("Callyzer Employee", {"employee_no": emp_number}):
            process_employee(emp)

        for log in emp.get("call_logs", []):
            if not frappe.db.exists("Callyzer Attendance Call", {"call_log": log["id"]}):
                doc = frappe.new_doc("Callyzer Attendance Call")
                doc.employee = emp_number
                doc.emp_code = emp.get("emp_code")
                doc.emp_name = emp.get("emp_name")
                doc.emp_number = emp_number
                doc.call_status = "Unattended"
                doc.client_name = emp.get("client_name")
                doc.client_number = emp.get("client_number")
                doc.call_log = log.get("id")
                doc.duration = log.get("duration")
                doc.call_type = log.get("call_type")
                doc.call_date = log.get("call_date")
                doc.call_time = log.get("call_time")
                doc.note = log.get("note")
                doc.call_recording_url = log.get("call_recording_url")
                doc.synced_at = log.get("synced_at")
                doc.modified_at = log.get("modified_at")
                doc.insert(ignore_permissions=True)

    frappe.db.commit()


#Fetch Not Pickup By Client.
@frappe.whitelist()
def fetch_not_pickup_by_client_calls():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

  
    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)
 
    url = f"{settings.domain_api}/call-log/not-pickup-by-client"
  
    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "emp_numbers": [],
        "emp_tags": [],
        "is_exclude_numbers": True,
        "page_no": 1,
        "page_size": 10
    }

    result = post_api(url, settings.api_key, payload)
    handle_not_pickup_by_client_calls(result)
  
    return {"status": "success", "message": "Analysis data inserted"}


def handle_not_pickup_by_client_calls(response):
    for emp in response:
        emp_number = emp.get("emp_number")
        if not emp_number:
            continue 

        # Ensure employee exists or process if not
        if not frappe.db.exists("Callyzer Employee", {"employee_no": emp_number}):
            process_employee(emp)

        for log in emp.get("call_logs", []):
            call_log_id = log.get("id")
            if not call_log_id:
                continue
            
            if not frappe.db.exists("Callyzer Attendance Call", {"call_log": call_log_id}):
                doc = frappe.new_doc("Callyzer Attendance Call")
                doc.employee = emp_number
                doc.emp_code = emp.get("emp_code")
                doc.emp_name = emp.get("emp_name")
                doc.emp_number = emp_number
                doc.call_status = "Missed"
                doc.client_name = emp.get("client_name")
                doc.client_number = emp.get("client_number")
                doc.call_log = call_log_id
                doc.duration = log.get("duration")
                doc.call_type = log.get("call_type")
                doc.call_date = log.get("call_date")
                doc.call_time = log.get("call_time")
                doc.note = log.get("note")
                doc.call_recording_url = log.get("call_recording_url")
                doc.synced_at = log.get("synced_at")
                doc.modified_at = log.get("modified_at")
                doc.insert(ignore_permissions=True)

# Fetch Unique Clients Report => Tested working fine
@frappe.whitelist()
def fetch_unique_clients_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

  
    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)
 
    url = f"{settings.domain_api}/call-log/unique-clients"
 
    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Incoming", "Outgoing"],
        "emp_numbers": [],
        "emp_tags": [],
        "is_exclude_numbers": True,
        "page_no": 1,
        "page_size": 100
    }

    result = post_api(url, settings.api_key, payload)
    process_unique_clients_response(result, company)
    
    return {"status": "success", "message": "Unique clients report fetched successfully"}

def process_unique_clients_response(result, company):
    clients = result
    inserted = 0

    for client in clients:
        if not (client.get("client_number") and client.get("client_country_code")):
            continue

        exists = frappe.db.exists("Callyzer Unique Client", {
            "client_number": client["client_number"],
            "client_country_code": client["client_country_code"],
            "company": company
        })
        if exists:
            continue

        doc = frappe.new_doc("Callyzer Unique Client")
        doc.client_name = client.get("client_name")
        doc.client_number = client.get("client_number")
        doc.client_country_code = client.get("client_country_code")
        doc.total_calls = client.get("total_calls")
        doc.total_incoming_calls = client.get("total_incoming_calls")
        doc.total_outgoing_calls = client.get("total_outgoing_calls")
        doc.company = company

        last_call_log = client.get("last_call_log", {})
        if last_call_log:
            doc.last_call_date = last_call_log.get("call_date")
            doc.last_call_time = last_call_log.get("call_time")
            doc.last_call_type = last_call_log.get("call_type")

        doc.insert(ignore_permissions=True)
        inserted += 1

    return {"status": "success", "inserted": inserted}


# Fetch Hourly Analytics Report
@frappe.whitelist()
def fetch_hourly_analytics_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)

    url = f"{settings.domain_api}/call-log/hourly-analytics"

    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "working_hour_from": "10:00",
        "working_hour_to": "11:00",
        "is_exclude_numbers": True
    }

    result =  post_api(url, settings.api_key, payload)
    process_hourly_analytics_response(result, company, start_date)
    return {"status": "success", "message": "Hourly analytics report fetched successfully"}
 

def process_hourly_analytics_response(result, company, call_date):
    result = result
    if not result:
        return {"status": "error", "message": "No result found in response"}

    total_calls = result.get("total_calls", 0)
    total_connected_calls = result.get("total_connected_calls", 0)
    total_duration = result.get("total_duration", 0)
    time_slots = result.get("time_slots", [])

    inserted = 0
    for slot in time_slots:
        doc = frappe.new_doc("Hourly Analytics")
        doc.company = company
        doc.call_date = call_date[:10]
        doc.hour = slot.get("hour")
        doc.call_count = slot.get("call_count", 0)
        doc.connected_call_count = slot.get("connected_call_count", 0)
        doc.duration = slot.get("duration", 0)
        doc.total_calls = total_calls
        doc.total_connected_calls = total_connected_calls
        doc.total_duration = total_duration
        doc.insert(ignore_permissions=True)
        inserted += 1

    return {
        "status": "success",
        "inserted": inserted,
        "total_slots": len(time_slots),
        "total_calls": total_calls,
        "total_connected_calls": total_connected_calls
    }

#Fetch Day-wise Analytics Report
@frappe.whitelist()
def fetch_day_wise_analytics_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)
  
    url = f"{settings.domain_api}/call-log/daywise-analytics"

    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "emp_numbers": [],
        "working_hour_from": "00:00",
        "working_hour_to": "20:59",
        "is_exclude_numbers": True
    }

    result = post_api(url, settings.api_key, payload)
    process_daywise_analytics_response(result, company)
    return {"status": "success", "message": "Day-wise analytics report fetched successfully"}
  
def process_daywise_analytics_response(response_json, company):
    result = response_json.get("result", {})
    if not result:
        return {"status": "error", "message": "No day-wise analytics found in response"}

    inserted = 0

    time_slots = result.get("time_slots", [])
    for slot in time_slots:
        day_wise_data = slot.get("day_wise", [])
        for row in day_wise_data:
            call_date = row.get("date")
            if not call_date:
                continue

            doc = frappe.new_doc("Daywise Analyicts")
            doc.company = company
            doc.call_date = call_date
            doc.total_calls = row.get("total_calls", 0)
            doc.total_connected_calls = row.get("total_connected_calls", 0)
            doc.total_duration = row.get("total_duration", 0)
            doc.insert(ignore_permissions=True)
            inserted += 1

    return {
        "status": "success",
        "inserted": inserted,
        "days_processed": inserted
    }

##Fetch Call History Report #Tested working
@frappe.whitelist()
def fetch_call_history_report():
    start_date = frappe.form_dict.get("start_date")
    end_date = frappe.form_dict.get("end_date")
    company = frappe.form_dict.get("company")

    call_from = format_time_timestamp_(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
    call_to = format_time_timestamp_(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S"))

    settings = get_callyzer_settings(company)
  
    url = f"{settings.domain_api}/call-log/history"

    payload = {
        "call_from": call_from,
        "call_to": call_to,
        "call_types": ["Missed", "Rejected", "Incoming", "Outgoing"],
        "emp_numbers": [],
        "is_exclude_numbers": True,
        "page_no": 1,
        "page_size": 100
    }
    result = post_api(url, settings.api_key, payload)
    process_call_history_response(result, company)
    return {"status": "success", "message": "Call history report fetched successfully"}
   

def process_call_history_response(result, company):
    call_logs = result
    if not call_logs:
        return {"status": "error", "message": "No call history data found in response"}

    inserted = 0
    for call in call_logs:
        if not (call.get("id") and call.get("client_number")):
            continue

        exists = frappe.db.exists("Call History Log", {
            "external_id": call["id"],
            "client_number": call["client_number"],
            "company": company
        })
        if exists:
            continue
        if not frappe.db.exists("Callyzer Employee", {"employee_no": call.get("emp_number")}):
                process_employee(call)

        doc = frappe.new_doc("Call History Log")
        doc.external_id = call.get("id")
        doc.emp_name = call.get("emp_name")
        doc.emp_code = call.get("emp_code")
        doc.emp_number = call.get("emp_number")
        doc.emp_country_code = call.get("emp_country_code")
        doc.emp_tags = ", ".join(call.get("emp_tags") or [])
        doc.client_name = call.get("client_name")
        doc.client_number = call.get("client_number")
        doc.client_country_code = call.get("client_country_code")
        doc.duration = call.get("duration")
        doc.call_type = call.get("call_type")
        doc.call_date = call.get("call_date")
        doc.call_time = call.get("call_time")
        doc.note = call.get("note")
        doc.call_recording_url = call.get("call_recording_url")
        doc.crm_status = call.get("crm_status")
        doc.reminder_date = call.get("reminder_date")
        doc.reminder_time = call.get("reminder_time")
        doc.synced_at = call.get("synced_at")
        doc.modified_at = call.get("modified_at")
        doc.lead_id = call.get("lead_id")
        doc.company = company

        doc.insert(ignore_permissions=True)
        inserted += 1

    return {
        "status": "success",
        "inserted": inserted,
        "records_fetched": len(call_logs)
    }

#Fetch Call History By Ids
@frappe.whitelist()
def fetch_call_history_by_ids():
    unique_ids = frappe.form_dict.get("unique_ids")
    company = frappe.form_dict.get("company")

    if not unique_ids or not isinstance(unique_ids, list):
        frappe.throw(_("Please provide a valid list of Unique IDs"))

    settings = get_callyzer_settings(company)
    if not settings:
        frappe.throw(_("Callyzer settings not found for the company"))

    url = f"{settings.domain_api}/call-log/get"
 
    payload = {
        "unique_ids": unique_ids
    }
    result = post_api(url, settings.api_key, payload)
    process_call_history_response(result, company)
    return {"status": "success", "message": "Call history fetched successfully"}
  
  
#Remove Call Recording
@frappe.whitelist()
def remove_call_recording(unique_ids: list[str], company: str = None):
    if not unique_ids:
        frappe.throw(_("Unique IDs are required"))

    settings = frappe.get_doc("Callyzer Settings", company)
    base_url = settings.api_url.rstrip("/")
    api_key = settings.api_key

    try:
        res = requests.delete(
            f"{base_url}/call-log/call-recording/remove",
            headers={"api-key": api_key},
            json={"unique_ids": unique_ids},
            timeout=30
        )
        res.raise_for_status()
        return {"status": "success", "message": res.json()}
    except requests.RequestException as e:
        frappe.log_error(f"Failed to remove call recording: {e}", "Callyzer Remove Call Recording")
        return {"status": "error", "message": str(e)}
    

#Tested working
@frappe.whitelist(allow_guest=True)
def callyzer_call_log_webhook():
    """Webhook endpoint for receiving and processing Callyzer employee & call log data."""
    try:
        if frappe.request.method != "POST":
            frappe.throw(_("Webhook only accepts POST requests"), frappe.ValidationError)

        payload = frappe.request.get_json()
        if not payload:
            frappe.throw(_("Invalid or empty JSON payload"))

        data = normalize_payload(payload)

        total_created = 0
        total_logs = 0

        for item in data:
            employee_name, is_new = process_employee(item)
            if is_new:
                total_created += 1

            logs_created = process_call_logs(employee_name, item.get("call_logs", []))
            total_logs += logs_created

        return {
            "status": "success",
            "employees_created": total_created,
            "call_logs_created": total_logs
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Webhook: Failed to process Callyzer data")
        return {"status": "error", "message": "Processing failed"}
    
    
def post_api(url, api_key, payload):
    headers = build_callyzer_headers(api_key)
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status()
        return response.json().get("result", {})
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Callyzer API Error"))
        frappe.throw(_("Failed to communicate with Callyzer API"))

def get_valid_callyzer_settings(company):
    settings = get_callyzer_settings(company)
    if not settings:
        frappe.throw(_("Callyzer settings not found for the company"))
    return settings

def build_callyzer_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    