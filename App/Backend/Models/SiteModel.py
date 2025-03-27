from typing import Optional
from App.Backend.Models.Model import Model

class SiteModel(Model):
    table_name = "sites"

    uuid: str
    nickname: Optional[str]
    online: bool
    mac_address: str
    ip_address: str

    # Set the unique field to ensure that inserts update on conflict.
    unique_field = "uuid"

    def to_dict(self) -> dict:
        """
        Convert the SiteModel object to a dictionary for JSON serialization.
        """
        return {
            "uuid": self.uuid,
            "nickname": self.nickname,
            "online": self.online,
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
        }
