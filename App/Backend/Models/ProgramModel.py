from typing import Optional

from App.Backend.Models.Model import Model
#from App.Backend.Server.ScoopFunctions import ScoopFunctions


class ProgramModel(Model):
    table_name = "installed_programs"

    client_uuid: str
    name: str
    current_version: str
    available_version: Optional[str]

    unique_field = "client_uuid,name"


    def find_available_version(self):
        #FIXME this will just take teh input from the server
        #version_number = ScoopFunctions.getSoftwareVersionNumber(self.name)
        #self.available_version = version_number
        self.save()


    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary for JSON serialization.
        """
        return {
            "client_uuid": self.client_uuid,
            "name": self.name,
            "current_version": self.current_version,
            "available_version": self.available_version
        }
