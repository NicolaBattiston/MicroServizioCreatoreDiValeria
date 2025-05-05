#!/usr/bin/env python3
import os
import yaml
import json
import logging
from pathlib import Path
logger = logging.getLogger(__name__)

def load_config():
    # 1) try your process’s working dir
    for name in ("config.yaml", "config.json"):
        cfg = Path(os.getcwd()) / name
        if cfg.is_file():
            return _parse_config(cfg)

    # 2) fallback to this module’s directory
    here = Path(__file__).parent
    for name in ("config.yaml", "config.json"):
        cfg = here / name
        if cfg.is_file():
            return _parse_config(cfg)

    raise FileNotFoundError("Configuration file (config.yaml or config.json) not found")

def _parse_config(path: Path):
    text = path.read_text()
    if path.suffix == ".yaml":
        return yaml.safe_load(text)
    else:
        return json.loads(text)
    required_fields = ['AES_KEY', 'WEBWALKER_URL', 'VALERIA_URL', 'NEXTOUT_TOKENS']
    missing = [f for f in required_fields if f not in config]
    if missing:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")
    return config
