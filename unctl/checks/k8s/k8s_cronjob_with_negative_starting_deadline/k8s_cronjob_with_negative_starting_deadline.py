from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_cronjob_with_negative_starting_deadline(Check):
    def _execute(self, cron, report) -> bool:
        if (cron.spec.starting_deadline_seconds is None) or (
            cron.spec.starting_deadline_seconds < 0
        ):
            report.status_extended = (
                f"Cronjob has starting deadline value as "
                f"({cron.spec.starting_deadline_seconds})"
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
