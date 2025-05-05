#!/usr/bin/env python3
import base64
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib.parse

logger = logging.getLogger(__name__)

def generate_custom_link(company_name: str, aes_key: str) -> str:
    key_bytes = bytes.fromhex(aes_key)
    cipher = AES.new(key_bytes, AES.MODE_CBC)
    data = pad(company_name.encode(), AES.block_size)
    ct = cipher.encrypt(data)
    token = base64.b64encode(cipher.iv + ct).decode()[:7]
    name_enc = urllib.parse.quote(company_name)
    link = f"https://provavaleria.sgaia.it/prova?nome={name_enc}&chiave={token}"
    logger.info(f"Generated custom link: {link}")
    return link
