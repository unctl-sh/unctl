import textwrap

from unctl.constants import CheckProviders
from unctl.lib.display.tables.base import BaseTable
from unctl.lib.display.tables.constants import TableNames
from unctl.lib.display.tables.decorators import header_processor
from unctl.lib.display.tables.utils import get_severity

__all__ = ["CommonChecksList"]


class CommonChecksList(
    BaseTable,
    providers=[CheckProviders.MySQL, CheckProviders.K8S],
    name=TableNames.LIST_CHECKS,
):
    HEADERS = [
        "Check",
        "Id",
        "Service",
        "Categories",
        "Severity",
        "Description",
    ]

    @header_processor("Severity")
    def get_check_severity(self, check, context):
        return get_severity(check)

    @header_processor("Check")
    def get_check_title(self, check, context):
        return textwrap.fill(check.check_metadata.CheckTitle, width=30)

    @header_processor("Id")
    def get_check_id(self, check, context):
        return textwrap.fill(check.check_metadata.CheckID, width=20)

    @header_processor("Service")
    def get_check_service(self, check, context):
        return textwrap.fill(check.check_metadata.SubServiceName, width=20)

    @header_processor("Categories")
    def get_check_categories(self, check, context):
        return textwrap.fill(",".join(check.check_metadata.Categories), width=30)

    @header_processor("Description")
    def get_check_description(self, check, context):
        descr_width = self.display.term_width - 115
        if descr_width < 30:
            descr_width = 30
        return textwrap.fill(check.check_metadata.Description, width=descr_width)
