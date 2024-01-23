from dataclasses import dataclass, field

from unctl.lib.checks.check_report import CheckReport


@dataclass
class CheckReportK8s(CheckReport):
    """Contains the AWS Check's finding information."""

    resource_id: str = ""
    resource_name: str = ""
    resource_namespace: str = ""
    resource_storageclass: str = ""
    resource_details: str = ""
    resource_tags: list = field(default_factory=list)
    resource_pod: str = ""
    resource_node: str = ""
    resource_cluster: str = ""
    resource_service: str = ""
    resource_pvc: str = ""
    resource_container: str = ""
    resource_selector: str = ""
    resource_dep_type: str = ""
    resource_dep_name: str = ""
    resource_configmap: str = ""

    @property
    def display_row(self):
        return [
            self.resource_namespace,
            self.resource_name,
            self.check_metadata.CheckTitle,
            self.check_metadata.Severity,
            self.status,
            self.status_extended,
        ]

    @property
    def object_id(self) -> str:
        return self.resource_id

    @property
    def object_name(self) -> str:
        return self.resource_name

    @property
    def unique_name(self) -> str:
        return f"{self.resource_namespace}/{self.resource_name}"

    @property
    def display_object(self) -> str:
        fmt_view = ""
        fmt_view += f'\n  "Status":  "{self.status}"'
        fmt_view += f'\n  "Check":  "{self.check_metadata.CheckTitle}"'
        fmt_view += f'\n  "Namespace":  "{self.resource_namespace}"'
        fmt_view += f'\n  "Object":  "{self.resource_name}"'
        fmt_view += f'\n  "Severity":  "{self.check_metadata.Severity}"'
        fmt_view += f'\n  "Summary":  "{self.status_extended}"'
        return fmt_view
