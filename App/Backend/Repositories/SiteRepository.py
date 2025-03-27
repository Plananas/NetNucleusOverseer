from typing import List, Optional
from App.Backend.Models.SiteModel import SiteModel

class SiteRepository:
    """Repository class for managing SiteModel interactions with the database."""

    @staticmethod
    def add_site(site: SiteModel) -> None:
        """Add a new site to the database."""
        site.save()

    @staticmethod
    def get_site_by_uuid(uuid: str) -> Optional[List[SiteModel]]:
        """Retrieve a site by its UUID."""
        return SiteModel.get(uuid=uuid)

    @staticmethod
    def get_site_by_mac_address(mac_address: str) -> Optional[List[SiteModel]]:
        """Retrieve a site by its MAC address."""
        return SiteModel.get(mac_address=mac_address)

    @staticmethod
    def get_site_by_nickname(nickname: str) -> Optional[SiteModel]:
        """Retrieve a site by its nickname."""
        sites = SiteModel.get(nickname=nickname)
        return sites[0] if sites else None

    @staticmethod
    def get_all_sites() -> List[SiteModel]:
        """Retrieve all sites from the database."""
        with SiteModel.get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {SiteModel.table_name}")
            rows = cursor.fetchall()
            field_names = [description[0] for description in cursor.description]
            return [SiteModel(**SiteModel._deserialize_row(dict(zip(field_names, row)))) for row in rows]

    @staticmethod
    def update_site(site: SiteModel) -> None:
        """Update an existing site in the database."""
        site.save()

    @staticmethod
    def delete_site_by_mac_address(mac_address: str) -> None:
        """Delete a site by its MAC address."""
        with SiteModel.get_connection() as conn:
            conn.execute(f"DELETE FROM {SiteModel.table_name} WHERE mac_address = ?", (mac_address,))
