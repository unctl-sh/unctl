from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_service_target_port_match(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for svc in data.get_services():
            report = CheckReportK8s(self.metadata())
            report.resource_id = svc.metadata.uid
            report.resource_name = svc.metadata.name
            report.resource_service = svc.metadata.name
            report.resource_namespace = svc.metadata.namespace

            svc_spec = svc.spec
            if svc_spec is not None and svc_spec.ports is not None:
                for port in svc_spec.ports:
                    if port.target_port != port.port:
                        report.status = "FAIL"
                        report.status_extended = (
                            f"Service port {port.port} "
                            "does not match target port {port.target_port}."
                        )
                        break
                else:
                    report.status = "PASS"
                    report.status_extended = (
                        "All service ports match their target ports."
                    )
            else:
                report.status = "FAIL"
                report.status_extended = "Service does not have ports specified."

            findings.append(report)

        return findings
