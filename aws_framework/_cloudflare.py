from ._config import cfg
from .client import ApiClient
from .utils import nginx_render


class CloudFlare(ApiClient):
    def __init__(self):
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "X-Auth-Email": cfg.CF_EMAIL,
            "X-Auth-Key": cfg.CF_API_KEY,
            "Content-Type": "application/json"
        }
        
    async def provision(self, name: str, port:int):
        """Provision a domain"""
        payload = {
            "type": "A",
            "name": name,
            "content": cfg.IP_ADDR,
            "ttl": 1,
            "proxied": True
        }
        response = await self.fetch(self.base_url+f"/{cfg.CF_ZONE_ID}/dns_records", method="POST", json=payload)
        nginx_render(name, port)
        return {
            "dns": response,
            "url": f"https://{name}.aiofauna.com"    
        }
        