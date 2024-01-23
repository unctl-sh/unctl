from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check
from croniter import croniter


class k8s_cronjobs_suspended_or_invalid_schedule(Check):
    def is_valid_cron_expression(self, cron_expression):
        try:
            croniter(cron_expression)
            return True
        except ValueError:
            return False

    def _execute(self, cron, report) -> bool:
        if self.is_valid_cron_expression(cron.spec.schedule) is False:
            report.status_extended = (
                f"Cron {cron.metadata.name} "
                f"in namespace {cron.metadata.namespace} "
                f"has invalid schedule {cron.spec.schedule}"
            )
            return False

        if cron.spec.suspend is not None and cron.spec.suspend is True:
            report.status_extended = (
                f"Cron {cron.metadata.name} in namespace "
                f"{cron.metadata.namespace} is suspended"
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for cron in data.get_cronjobs():
            report = CheckReportK8s(self.metadata())
            report.resource_id = cron.metadata.uid
            report.resource_name = cron.metadata.name
            report.resource_namespace = cron.metadata.namespace
            report.status = "PASS"

            if not self._execute(cron, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
