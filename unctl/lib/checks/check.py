import json
import os
import sys
from abc import ABC, abstractmethod

from unctl.lib.models.checks import CheckMetadataModel
from unctl.lib.checks.check_report import CheckReport


class Check(ABC, CheckMetadataModel):
    def __init__(self, **data):
        """Check's init function. Calls the CheckMetadataModel init."""
        # Parse the Check's metadata file
        metadata_file = (
            os.path.abspath(sys.modules[self.__module__].__file__)[:-3] + ".json"
        )

        with open(metadata_file, "r") as md_file:
            metadata = json.load(md_file)

        # Store it to validate them with Pydantic
        data = CheckMetadataModel.model_validate_json(json.dumps(metadata)).model_dump()

        # Calls parents init function
        super().__init__(**data)

        self._metadata_file = metadata_file

    def metadata(self) -> str:
        """Return the JSON representation of the check's metadata"""
        return self.model_dump_json()

    @abstractmethod
    def execute(self, data) -> list[CheckReport]:
        """Execute the check's logic"""
