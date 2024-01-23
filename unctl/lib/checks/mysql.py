from dataclasses import dataclass

from unctl.lib.checks.check_report import CheckReport


@dataclass
class CheckReportMySQL(CheckReport):
    resource_name: str = "global"
    resource_id: str = ""

    @property
    def display_row(self):
        return [
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
    def display_object(self) -> str:
        fmt_view = ""
        fmt_view += f'\n  "Status":  "{self.status}"'
        fmt_view += f'\n  "Check":  "{self.check_metadata.CheckTitle}"'
        fmt_view += f'\n  "Object":  "{self.resource_name}"'
        fmt_view += f'\n  "Severity":  "{self.check_metadata.Severity}"'
        fmt_view += f'\n  "Summary":  "{self.status_extended}"'
        return fmt_view
