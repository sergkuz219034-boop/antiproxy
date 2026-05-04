import requests
from app.config import settings

class AdsPowerClient:
    def __init__(self):
        self.base_url = settings.ADSPOWER_API_URL

    def check_status(self):
        try:
            res = requests.get(f"{self.base_url}/status", timeout=2) # AdsPower status API
            return res.ok
        except:
            return False

    def get_profiles(self):
        try:
            res = requests.get(f"{self.base_url}/api/v1/user/list")
            if res.ok:
                return res.json().get("data", {}).get("list", [])
        except:
            pass
        return []

    def create_profile(self, name, proxy=None):
        payload = {
            "name": name,
            "domain_name": "google.com",
        }
        if proxy:
            payload["user_proxy_config"] = {
                "proxy_soft": "other",
                "proxy_type": proxy.protocol,
                "proxy_host": proxy.host,
                "proxy_port": proxy.port,
                "proxy_user": proxy.username,
                "proxy_password": proxy.password
            }
        
        try:
            res = requests.post(f"{self.base_url}/api/v1/user/create", json=payload)
            if res.ok:
                return res.json().get("data", {}).get("id")
        except:
            pass
        return None

    def start_profile(self, adspower_id):
        try:
            res = requests.get(f"{self.base_url}/api/v1/browser/start", params={"user_id": adspower_id})
            if res.ok:
                return res.json().get("data", {})
        except:
            pass
        return None

    def stop_profile(self, adspower_id):
        try:
            res = requests.get(f"{self.base_url}/api/v1/browser/stop", params={"user_id": adspower_id})
            return res.ok
        except:
            return False

adspower = AdsPowerClient()
