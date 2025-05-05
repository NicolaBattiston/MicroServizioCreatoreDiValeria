#!/usr/bin/env python3
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MockWebWalkerService:
    def __init__(self):
        logger.info("Initialized MockWebWalkerService")
    def simulate_success(self, job_id: str) -> Dict[str, Any]:
        return {"job_id": job_id, "company_id": f"comp-{job_id[:8]}", "company_name": job_id, "company_sector": "Tech"}
    def simulate_timeout(self, job_id: str):
        time.sleep(2)
        raise TimeoutError("Simulated timeout")
    def simulate_error(self, job_id: str):
        raise Exception("Simulated error")
