from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pvc_pending(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def create_jobs(self):
        # You might or might not need this depending on your structure
        return None

    def _execute(self, pvc, report) -> bool:
        # Check PVC status
        if pvc.status.phase == "Pending":
            report.status_extended = (
                f"PVC {pvc.metadata.name} "
                f"in namespace {pvc.metadata.namespace} is in Pending state."
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        # Iterate over each PVC
        for pvc in data.get_pvcs():
            report = CheckReportK8s(self.metadata())

            # Populate report details
            report.resource_id = pvc.metadata.uid
            report.resource_name = pvc.metadata.name
            report.resource_pvc = pvc.metadata.name  # New field you might want to add
            report.resource_namespace = pvc.metadata.namespace
            report.status = "PASS"

            if not self._execute(pvc, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
