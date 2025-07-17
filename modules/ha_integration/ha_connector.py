"""
Phase 181: HA OS Intent Bridge
Maps voice intents → adaptive_router + decision tree.
"""
import requests, os

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

def install_addon():
    url = f"{HA_URL}/api/hassio/addons/sterling_os/install"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    requests.post(url, headers=headers)
