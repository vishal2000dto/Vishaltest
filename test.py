import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

url = "http://localhost:8081/api/v1/chat/virtual_agent_experimental/d9b7eae9-3fe8-400f-aa85-48667b616daa"
headers = {"Content-Type": "application/json"}

payload = {
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False,
    "user": {
        "employee_id": None,
        "employee_name": None,
        "email": None,
        "phone_number": None,
        "total_storage": None,
        "free_storage": None,
        "percentage_available": None,
        "operating_system": None,
        "existing_apps_by_name": None,
    },
    "context": {
        "overrides": {
            "top": 7,
            "retrieval_mode": "vectors",
            "session_id": None,
            "app_id": None,
            "semantic_ranker": True,
            "semantic_captions": False,
            "suggest_followup_questions": False,
            "use_oid_security_filter": False,
            "use_groups_security_filter": False,
            "vector_fields": ["embedding"],
            "use_gpt4v": False,
            "gpt4v_input": "",
            "ticket_id": None,
            "call_transcript": None,
            "ticket_details": {},  # FIXED
            "category": None,
            "module": None,
            "chat_type": None,
            "kb": None,
        }
    },
    "session_state": {},  # FIXED
    "org_id": "d9b7eae9-3fe8-400f-aa85-48667b616daa",
}


def send_post_request(index):
    try:
        print(f"[{index}] Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        print(f"SUCCESS:[{index}] {response.status_code} - {response.text[:100]}")
        return f"[{index}] {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"[{index}] ERROR: {e}"


with ThreadPoolExecutor(max_workers=2) as executor:
    futures = []
    for i in range(1, 2):
        futures.append(executor.submit(send_post_request, i))
        time.sleep(0.1)  # Add 100ms delay between submitting each request

    for future in as_completed(futures):
        print(future.result())




