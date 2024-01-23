from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_service_with_notready_endpoints(Check):
    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        endpoints = data.get_endpoints()
        for service in data.get_services():
            report = CheckReportK8s(self.metadata())
            report.resource_id = service.metadata.uid
            report.resource_name = service.metadata.name
            report.resource_service = service.metadata.name
            report.resource_namespace = service.metadata.namespace
            report.status = "PASS"

            for endpoint in endpoints:
                if endpoint.metadata.name == service.metadata.name and endpoint.subsets:
                    not_ready = 0
                    for subset in endpoint.subsets:
                        if subset.not_ready_addresses:
                            not_ready += len(subset.not_ready_addresses)

                    if not_ready > 0:
                        report.status = "FAIL"
                        report.status_extended = "Service has NotReady endpoints"

                        # populate the selector for diagnostics
                        s = []
                        for k, v in service.spec.selector.items():
                            s.append(f"{k}={v}")
                        report.resource_selector = ",".join(s)

                    break

            findings.append(report)

        return findings
