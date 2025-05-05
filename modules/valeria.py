#!/usr/bin/env python3
import logging
import time
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ValeriaError(Exception):
    pass

def configure_company(data: Dict[str, Any], valeria_url: str) -> None:
    payload = {
        "username": data['company_name'],
        "company_sector": data['company_sector'],
        "communication_techniques": data.get('communication_techniques'),
        "security_policy": data.get('security_policy')
    }
    url = f"{valeria_url.rstrip('/')}/company_config"
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code not in (200,201,202):
        raise ValeriaError(f"{r.status_code}")
    logger.info("Company configured")

def import_vector_json(company_id: str, vector_data: Dict[str, Any], valeria_url: str, max_retries: int = 3) -> None:
    url = f"{valeria_url.rstrip('/')}/company_config/{company_id}/import_json"
    attempts, backoff = max_retries, 2
    for i in range(attempts):
        r = requests.post(url, json=vector_data, timeout=60)
        if r.status_code in (200,201,202):
            logger.info("Imported vector data")
            return
        time.sleep(backoff**i)
    raise ValeriaError("Failed import after retries")
