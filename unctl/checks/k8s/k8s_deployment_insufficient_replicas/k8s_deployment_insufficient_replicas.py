from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_deployment_insufficient_replicas(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def create_jobs(self):
        return None

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for deployment in data.get_deployments():
            report = CheckReportK8s(self.metadata())
            report.resource_id = deployment.metadata.uid
            report.resource_name = deployment.metadata.name
            report.resource_namespace = deployment.metadata.namespace
            report.status = "PASS"

            # Check if the desired replica count
            # matches the available replica count
            if deployment.spec.replicas != deployment.status.available_replicas:
                report.status = "FAIL"
                report.status_extended = (
                    f"Deployment {deployment.metadata.name} has "
                    f"{deployment.status.available_replicas} replicas available "
                    f"out of {deployment.spec.replicas} desired."
                )
                findings.append(report)

            if report.status == "PASS":
                findings.append(report)

        return findings
