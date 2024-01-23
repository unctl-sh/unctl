import textwrap

from colorama import Fore, Style

from unctl.constants import CheckProviders
from unctl.lib.display.tables.base import BaseTable
from unctl.lib.display.tables.constants import TableNames
from unctl.lib.display.tables.decorators import header_processor
from unctl.lib.display.tables.utils import get_severity

__all__ = ["K8SSortedByObject", "K8SSortedByChecks"]


class K8SSortedByObject(
    BaseTable, providers=[CheckProviders.K8S], name=TableNames.SORTED_BY_OBJECT
):
    HEADERS = [
        "Resource Namespace",
        "Resource Name",
        "Check Title",
        "Status",
        "Severity",
        "Status Extended",
    ]

    @classmethod
    def configure(
        cls, results, display, context=None, initial_table=None, divider=False
    ):
        grouped_results = {}
        for result in results:
            grouped_results.setdefault(result.resource_namespace, {}).setdefault(
                result.resource_name, []
            ).append(result)
        results = sum(
            [
                group
                for resource_group in grouped_results.values()
                for group in resource_group.values()
            ],
            [],
        )
        sorted_results = sorted(
            results, key=lambda check: (check.resource_namespace, check.resource_name)
        )
        return super().configure(
            sorted_results, display, context, initial_table, divider
        )

    @header_processor("Resource Namespace")
    def get_resource_namespace(self, check, context):
        return check.resource_namespace.ljust(20)

    @header_processor("Resource Name")
    def get_resource_name(self, check, context):
        return textwrap.fill(check.resource_name, width=20)

    @header_processor("Check Title")
    def get_check_title(self, check, context):
        return textwrap.fill(check.check_metadata.CheckTitle, width=30)

    @header_processor("Status")
    def get_check_status(self, check, context):
        return check.status.center(10)

    @header_processor("Severity")
    def get_check_severity(self, check, context):
        return check.check_metadata.Severity.center(10)

    @header_processor("Status Extended")
    def get_check_status_extended(self, check, context):
        return textwrap.fill(check.status_extended, width=60)


class K8SSortedByChecks(
    BaseTable, providers=[CheckProviders.K8S], name=TableNames.SORTED_BY_CHECKS
):
    HEADERS = [
        "Resource Namespace",
        "Resource Name",
        "Status",
        "Severity",
        "Status Extended",
    ]

    # this is unique to this table, only part that the base table respects is `HEADERS`
    WIDTH_CONFIG = {
        "Resource Namespace": 30,
        "Resource Name": 30,
        "Status": 10,
        "Severity": 10,
        "Status Extended": 70,
    }

    @classmethod
    def configure(
        cls, results, display, context=None, initial_table=None, divider=False
    ):
        instance = super().configure(results, display, context, initial_table, divider)
        instance.initial_table._max_width = cls.WIDTH_CONFIG
        return instance

    @header_processor("Resource Namespace")
    def get_resource_namespace(self, check, context):
        resource_namespace_wrapped = textwrap.fill(
            check.resource_namespace,
            width=self.WIDTH_CONFIG.get("Resource Namespace", 0),
        )
        resource_namespace_wrapped = self.display.center_content(
            resource_namespace_wrapped,
            self.WIDTH_CONFIG.get("Resource Namespace", 0),
        )
        return resource_namespace_wrapped

    @header_processor("Resource Name")
    def get_resource_name(self, check, context):
        resource_name_wrapped = textwrap.fill(
            check.resource_name, width=self.WIDTH_CONFIG.get("Resource Name", 0)
        )
        resource_name_wrapped = self.display.center_content(
            resource_name_wrapped, self.WIDTH_CONFIG.get("Resource Name", 0)
        )
        return resource_name_wrapped

    @header_processor("Status")
    def get_check_status(self, check, context):
        status = Fore.RED + check.status + Style.RESET_ALL
        status = self.display.center_content(status, self.WIDTH_CONFIG.get("Status", 0))
        return status

    @header_processor("Severity")
    def get_check_severity(self, check, context):
        severity = self.display.center_content(
            get_severity(check), self.WIDTH_CONFIG.get("Severity", 0)
        )
        return severity

    @header_processor("Status Extended")
    def get_check_status_extended(self, check, context):
        return self._wrap_extended_status(check.status_extended)

    def _wrap_extended_status(self, status):
        # Wrap the content based on max widths
        status_extended_wrapped = textwrap.fill(
            status, width=self.WIDTH_CONFIG.get("Status Extended", 0)
        )
        status_extended_wrapped = self.display.center_content(
            status_extended_wrapped, self.WIDTH_CONFIG.get("Status Extended", 0)
        )
        return status_extended_wrapped
