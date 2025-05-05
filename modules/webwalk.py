#!/usr/bin/env python3
import logging
import time
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebWalkerError(Exception):
    pass

class WebWalkerTimeoutError(TimeoutError):
    pass

def start_webwalk(job_id: str, webwalker_url: str, timeout: int = 180) -> Dict[str, Any]:
    start_url = f"{webwalker_url.rstrip('/')}"
    r = requests.post(start_url, json={"job_id": job_id}, timeout=10)
    if r.status_code != 202:
        raise WebWalkerError(f"Failed start: {r.status_code}")
    status_url = f"{webwalker_url.rstrip('/')}/status/{job_id}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        r = requests.get(status_url, timeout=10)
        if r.status_code == 200:
            return r.json()
        time.sleep(5)
    raise WebWalkerTimeoutError(f"Timeout after {timeout}s")

class MockWebWalker:
    def __init__(self):
        logger.info("Initialized MockWebWalker")
    def process_job(self, job_id: str) -> Dict[str, Any]:
        return {
            "job_id": job_id,
            "company_id": f"comp-{job_id[:8]}",
            "company_name": f"TestCo-{job_id[:4]}",
            "company_sector": "Tech",
            "communication_techniques": [],
            "security_policy": {},
            "vector_data": {}
        }
