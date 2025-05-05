#!/usr/bin/env python3
import os
import yaml
import json
import logging

logger = logging.getLogger(__name__)

def load_config():
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            logger.info("Loaded configuration from config.yaml")
    elif os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
            logger.info("Loaded configuration from config.json")
    else:
        raise FileNotFoundError("Configuration file (config.yaml or config.json) not found")
    
    required_fields = ['AES_KEY', 'WEBWALKER_URL', 'VALERIA_URL', 'NEXTOUT_TOKENS']
    missing = [f for f in required_fields if f not in config]
    if missing:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")
    return config
