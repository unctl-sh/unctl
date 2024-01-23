from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_service_empty(Check):
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

            service_endpoints = [
                ep
                for ep in endpoints
                if ep.metadata.name == service.metadata.name and ep.subsets
            ]

            if len(service_endpoints) == 0:
                report.status = "FAIL"
                report.status_extended = "Service has NO endpoints"

                # populate the selector for diagnostics
                s = []
                for k, v in service.spec.selector.items():
                    s.append(f"{k}={v}")
                report.resource_selector = ",".join(s)

            findings.append(report)

        return findings
