from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pods_pending(Check):
    def _execute(self, pod, report):
        if pod.status.phase != "Pending":
            return True
        else:
            for condition in pod.status.conditions:
                report.status_extended = (
                    f"Pod is in Pending state as the pod condition is "
                    f"'{condition.reason}'"
                )
                return False

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_pod = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace
            report.status = "PASS"

            if not self._execute(pod, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
