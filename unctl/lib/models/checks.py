from dataclasses import field

from pydantic import BaseModel


class CheckMetadataModel(BaseModel):
    """
    Check Metadata Model. It contains metadata from individual check json config
    """

    Enabled: bool = field(default=True)
    Provider: str
    CheckID: str
    CheckTitle: str
    CheckType: list[str]
    ServiceName: str
    SubServiceName: str
    ResourceIdTemplate: str
    Severity: str
    ResourceType: str
    Description: str
    Risk: str
    RelatedUrl: str
    Categories: list[str]
    DependsOn: list[str]
    RelatedTo: list[str]
    Notes: str
    PositiveMatch: str
    NegativeMatch: str
