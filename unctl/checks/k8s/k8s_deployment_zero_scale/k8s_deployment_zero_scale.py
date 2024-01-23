from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_deployment_zero_scale(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for deployment in data.get_deployments():
            report = CheckReportK8s(self.metadata())
            report.resource_id = deployment.metadata.uid
            report.resource_name = deployment.metadata.name
            report.resource_namespace = deployment.metadata.namespace

            replicas = deployment.spec.replicas

            if replicas == 0:
                report.status = "FAIL"
                report.status_extended = (
                    f"Deployment {deployment.metadata.name} is scaled to zero."
                )
            else:
                report.status = "PASS"
                report.status_extended = (
                    f"Deployment {deployment.metadata.name} "
                    "has a non-zero replica count."
                )

            findings.append(report)

        return findings
