from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_service_pod_label_match(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        # Assuming services and pods have been collected from the cluster
        services = data.get_services()
        pods = data.get_pods()

        for service in services:
            report = CheckReportK8s(self.metadata())
            report.resource_id = service.metadata.uid
            report.resource_name = service.metadata.name
            report.resource_service = service.metadata.name
            report.resource_namespace = service.metadata.namespace

            # Get selectors from the service to match pods
            service_selectors = service.spec.selector

            # If the service has no selectors, it will not have matching pods
            if not service_selectors:
                report.status = "FAIL"
                report.status_extended = (
                    f"Service {service.metadata.name} does"
                    " not have any selectors for pods."
                )
                findings.append(report)
                continue

            # Check if any pod matches the service selectors
            matching_pods = [
                pod
                for pod in pods
                if self.matches_service_selectors(pod, service_selectors)
            ]

            if matching_pods:
                report.status = "PASS"
                report.status_extended = (
                    f"Service {service.metadata.name} has"
                    " matching pods with its selectors."
                )
            else:
                report.status = "FAIL"
                report.status_extended = (
                    f"Service {service.metadata.name} does "
                    "not have any matching pods with its selectors."
                )

            findings.append(report)

        return findings

    def matches_service_selectors(self, pod, service_selectors):
        if not pod.metadata.labels:
            return False
        return all(
            label in pod.metadata.labels.items() for label in service_selectors.items()
        )
