import sys
import os
import json
import logging
from collections import defaultdict

# Logging ko configure karo taaki warnings aur errors stderr pe print ho
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def parse_log_line(line):
    """
    Ye code ek single log line ko parse karta hai.
    Expected format:
    <timestamp> - FLOW: <flow_id> - API: <endpoint> - STATUS: <status> [- ERROR: <error_message>]
    Agar line properly formatted hai toh parsed fields ka ek dictionary return karega, nahi toh None return karega.
    """
    try:
        # Line ko `' - '` se split karo jo log ke alag-alag parts ko separate karta hai.
        parts = line.strip().split(" - ")
        if len(parts) < 4:
            raise ValueError("Log line me required parts nahi hain")

        # Timestamp extract karo (pehla part)
        timestamp = parts[0]

        # Flow ID extract karo (jo "FLOW: <flow_id>" format me hota hai)
        flow_part = parts[1].strip()
        if not flow_part.startswith("FLOW: "):
            raise ValueError("FLOW identifier missing hai")
        flow_id = flow_part.split("FLOW: ")[1]

        # API endpoint extract karo (jo "API: <endpoint>" format me hota hai)
        api_part = parts[2].strip()
        if not api_part.startswith("API: "):
            raise ValueError("API identifier missing hai")
        api_endpoint = api_part.split("API: ")[1]

        # Status extract karo (jo "STATUS: <status>" format me hota hai)
        status_part = parts[3].strip()
        if not status_part.startswith("STATUS: "):
            raise ValueError("STATUS missing hai")
        status = status_part.split("STATUS: ")[1]

        # Agar API call fail hui ho toh error message extract karo
        error_message = None
        if status.upper() == "FAILED" and len(parts) > 4:
            error_part = parts[4].strip()
            if error_part.startswith("ERROR: "):
                error_message = error_part.split("ERROR: ")[1]
        
        return {
            "timestamp": timestamp,
            "flow_id": flow_id,
            "api_endpoint": api_endpoint,
            "status": status.upper(),
            "error_message": error_message
        }
    except Exception as e:
        logging.warning(f"Galat formatted line skip ho rahi hai: {line.strip()} | Error: {e}")
        return None

def process_log_files(file_paths):
    """
    Multiple log files process karta hai aur test flow aur API failure ka data aggregate karta hai.
    Ek dictionary return karta hai jo aggregated report contain karti hai.
    """
    flows = {}  # Flow ID ka mapping jisme failure count aur failed APIs ki list hogi
    api_failures = defaultdict(int)  # Har API endpoint ke failures count karta hai
    
    # Har file process karo
    for file_path in file_paths:
        if not os.path.exists(file_path):
            logging.error(f"File nahi mili: {file_path}")
            continue
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue  # Empty lines ko skip karo
                    entry = parse_log_line(line)
                    if entry is None:
                        continue  # Agar line parsing fail hui toh skip karo
                    flow_id = entry["flow_id"]
                    # Agar ye flow pehli baar mila toh initialize karo
                    if flow_id not in flows:
                        flows[flow_id] = {
                            "total_calls": 0,
                            "failed_calls": 0,
                            "failed_api_details": defaultdict(int)
                        }
                    flows[flow_id]["total_calls"] += 1
                    # Agar API call fail hui toh failure count update karo
                    if entry["status"] == "FAILED":
                        flows[flow_id]["failed_calls"] += 1
                        flows[flow_id]["failed_api_details"][entry["api_endpoint"]] += 1
                        api_failures[entry["api_endpoint"]] += 1
        except Exception as e:
            logging.error(f"File read karne me error: {file_path} | Error: {e}")
    
    # Flow ka overall status determine karo
    total_flows = len(flows)
    failed_flows = {fid: details for fid, details in flows.items() if details["failed_calls"] > 0}
    passing_flows = {fid: details for fid, details in flows.items() if details["failed_calls"] == 0}

    # Sabse zyada failures wale flow aur API endpoint ko identify karo
    top_failed_flow = None
    max_flow_failures = -1
    for fid, details in flows.items():
        if details["failed_calls"] > max_flow_failures:
            max_flow_failures = details["failed_calls"]
            top_failed_flow = fid

    top_failed_api = None
    max_api_failures = -1
    for api, count in api_failures.items():
        if count > max_api_failures:
            max_api_failures = count
            top_failed_api = api

    # Final report banaye
    report = {
        "total_flows": total_flows,
        "passing_flows_count": len(passing_flows),
        "failed_flows_count": len(failed_flows),
        "flows": flows,
        "api_failures": dict(api_failures),
        "top_failed_flow": {
            "flow_id": top_failed_flow,
            "failed_calls": max_flow_failures
        } if top_failed_flow is not None else {},
        "top_failed_api": {
            "api_endpoint": top_failed_api,
            "failure_count": max_api_failures
        } if top_failed_api is not None else {}
    }
    
    return report

def main():
    """
    Command line arguments process karta hai aur test log report generate karta hai.
    """
    if len(sys.argv) < 2:
        print("Usage: python analyze_logs.py <log_file1> [<log_file2> ...]")
        sys.exit(1)
    
    file_paths = sys.argv[1:]
    report = process_log_files(file_paths)
    
    # Final report ko JSON format me print karo
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()