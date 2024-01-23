from typing import ClassVar

from unctl.lib.checks.check import Check
from unctl.lib.checks.check_report import CheckReport
from unctl.lib.checks.mysql import CheckReportMySQL


class mysql_max_used_connections(Check):
    DEFAULT_THRESHOLD: ClassVar[int] = 80  # %

    def _execute(self, max_connections, connections_used, report):
        percentage_used = 100 * connections_used / max_connections
        if percentage_used >= self.DEFAULT_THRESHOLD:
            report.status_extended = (
                f"Used high value of database connections ({percentage_used}%): "
                f"{connections_used} of {max_connections} available"
            )
            return False
        return True

    async def execute(self, data) -> list[CheckReport]:
        max_connections = await data.get_max_connections()
        connections_used = await data.get_connections_used()
        report = CheckReportMySQL(self.metadata())
        report.resource_id = "Max_used_connections"
        report.resource_name = "MySQL"
        report.status = "PASS"

        if not self._execute(max_connections, connections_used, report):
            report.status = "FAIL"

        return [report]
