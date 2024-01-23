from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_statefulset_zero_scale(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        statefulsets = data.get_statefulsets()

        for ss in statefulsets:
            report = CheckReportK8s(self.metadata())
            report.resource_id = ss.metadata.uid
            report.resource_namespace = ss.metadata.namespace
            report.resource_name = ss.metadata.name

            # Check if the StatefulSet replicas count is 0
            if ss.spec.replicas is not None and ss.spec.replicas <= 0:
                report.status = "FAIL"
                report.status_extended = (
                    f"StatefulSet {ss.metadata.name} is scaled to 0."
                )
            else:
                report.status = "PASS"
                report.status_extended = (
                    f"StatefulSet {ss.metadata.name} is scaled above 0."
                )

            findings.append(report)

        return findings
