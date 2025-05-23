import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    columns = [
        {"label": "Date", "fieldname": "call_date", "fieldtype": "Date", "width": 100},
        {"label": "Total Calls", "fieldname": "total_calls", "fieldtype": "Int", "width": 120},
        {"label": "Total Connected Calls", "fieldname": "total_connected_calls", "fieldtype": "Int", "width": 150},
        {"label": "Total Duration", "fieldname": "total_duration", "fieldtype": "Float", "width": 120},
    ]

    hours = ["Before 10:00 AM"] + [f"{str(h).zfill(2)}:00" for h in range(10, 20)] + ["After 07:00 PM"]

    for hour in hours:
        suffix = normalize_slot(hour)
        columns.extend([
            {"label": f"{hour} - Calls", "fieldname": f"calls_{suffix}", "fieldtype": "Int", "width": 110},
            {"label": f"{hour} - Connected", "fieldname": f"connected_{suffix}", "fieldtype": "Int", "width": 120},
            {"label": f"{hour} - Duration", "fieldname": f"duration_{suffix}", "fieldtype": "Float", "width": 110},
        ])
    return columns


def normalize_slot(slot):
    if slot == "Before 10:00 AM":
        return "before_10"
    if slot == "After 07:00 PM":
        return "after_1900"
    if ":00" in slot:
        return slot.replace(":", "")[:4]
    return slot.lower().replace(":", "").replace(" ", "_")


def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    raw_data = frappe.db.sql("""
        SELECT 
            call_date,
            slot,
            SUM(total_calls) AS total_calls,
            SUM(total_connected_calls) AS total_connected_calls,
            SUM(total_duration) AS total_duration
        FROM `tabDaywise Analyicts`
        WHERE call_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY call_date, slot
        ORDER BY call_date ASC
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    structured = {}
    for row in raw_data:
        date = row["call_date"]
        slot_suffix = normalize_slot(row["slot"])

        if date not in structured:
            structured[date] = {}

        structured[date][slot_suffix] = {
            "calls": row["total_calls"],
            "connected": row["total_connected_calls"],
            "duration": row["total_duration"]
        }

    slots = ["before_10"] + [f"{str(h).zfill(2)}00" for h in range(10, 20)] + ["after_1900"]

    result = []
    totals = {"total_calls": 0, "total_connected_calls": 0, "total_duration": 0}
    slot_totals = {slot: {"calls": 0, "connected": 0, "duration": 0} for slot in slots}

    for date, slot_data in structured.items():
        row = {
            "call_date": date,
            "total_calls": sum(v["calls"] for v in slot_data.values()),
            "total_connected_calls": sum(v["connected"] for v in slot_data.values()),
            "total_duration": sum(v["duration"] for v in slot_data.values()),
        }

        for slot in slots:
            data = slot_data.get(slot, {"calls": 0, "connected": 0, "duration": 0})
            row[f"calls_{slot}"] = data["calls"]
            row[f"connected_{slot}"] = data["connected"]
            row[f"duration_{slot}"] = data["duration"]

            # accumulate slot totals
            slot_totals[slot]["calls"] += data["calls"]
            slot_totals[slot]["connected"] += data["connected"]
            slot_totals[slot]["duration"] += data["duration"]

        totals["total_calls"] += row["total_calls"]
        totals["total_connected_calls"] += row["total_connected_calls"]
        totals["total_duration"] += row["total_duration"]

        result.append(row)

    # Add Total row
    total_row = {
        "call_date": "Total",
        "total_calls": totals["total_calls"],
        "total_connected_calls": totals["total_connected_calls"],
        "total_duration": totals["total_duration"]
    }
    for slot in slots:
        total_row[f"calls_{slot}"] = slot_totals[slot]["calls"]
        total_row[f"connected_{slot}"] = slot_totals[slot]["connected"]
        total_row[f"duration_{slot}"] = slot_totals[slot]["duration"]
    result.append(total_row)

    # Add Average row
    num_days = len(structured)
    if num_days > 0:
        avg_row = {
            "call_date": "Average",
            "total_calls": round(totals["total_calls"] / num_days, 2),
            "total_connected_calls": round(totals["total_connected_calls"] / num_days, 2),
            "total_duration": round(totals["total_duration"] / num_days, 2)
        }
        for slot in slots:
            avg_row[f"calls_{slot}"] = round(slot_totals[slot]["calls"] / num_days, 2)
            avg_row[f"connected_{slot}"] = round(slot_totals[slot]["connected"] / num_days, 2)
            avg_row[f"duration_{slot}"] = round(slot_totals[slot]["duration"] / num_days, 2)
        result.append(avg_row)

    return result

def get_chart(data, filters=None):
    labels = []
    total_calls = []
    total_connected = []

    for row in data:
        if isinstance(row["call_date"], str) and row["call_date"] in ["Total", "Average"]:
            continue
        labels.append(str(row["call_date"]))
        total_calls.append(row.get("total_calls", 0))
        total_connected.append(row.get("total_connected_calls", 0))

    chart_type = (filters.get("chart_type") or "Bar").lower()  # default to bar if none

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Total Calls",
                    "values": total_calls,
                    "color": "#006400"
                },
                {
                    "name": "Connected Calls",
                    "values": total_connected,
                    "color": "#FFA500"
                }
            ]
        },
        "type": chart_type,  # "bar" or "line"
        "barOptions": {
            "stacked": False
        } if chart_type == "bar" else {}
    }
