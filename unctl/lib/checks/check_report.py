import abc
from dataclasses import dataclass, field, InitVar
from typing import Literal

from unctl.lib.models.checks import CheckMetadataModel


@dataclass
class CheckReport:
    """Contains the Check's finding information."""

    raw_metadata: InitVar[str | bytes]

    check_metadata: CheckMetadataModel = field(init=False)

    status: Literal["PASS", "FAIL"] | None = None
    status_extended: str = ""
    module: str = ""

    def __post_init__(self, raw_metadata):
        self.check_metadata = CheckMetadataModel.model_validate_json(raw_metadata)

    @property
    def passed(self):
        return self.status == "PASS"

    @property
    @abc.abstractmethod
    def display_object(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def display_row(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def object_id(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def object_name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unique_name(self) -> str:
        """Returns unique name of failed object"""
