from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_ingress(Check):
    def _execute(self, ingress, services, secrets, ingress_classes, report) -> bool:
        ingress_name = ingress.metadata.name
        ingress_class_name = getattr(ingress.spec, "ingress_class_name", None)
        ingress_namespace = ingress.metadata.namespace

        if not ingress_class_name:
            ingress_class_value = ingress.metadata.annotations.get(
                "kubernetes.io/ingress.class"
            )
            if not ingress_class_value:
                report.status_extended = (
                    f"Ingress {ingress_namespace}/{ingress_name} "
                    "is missing an Ingress "
                    f"class configuration."
                )
                return False

            ingress_class_name = ingress_class_value

        ingress_class_info = {(s.metadata.name) for s in ingress_classes}
        service_info = {(s.metadata.name, s.metadata.namespace) for s in services}
        secrets_info = {(s.metadata.name, s.metadata.namespace) for s in secrets}
        non_existent_services = [
            path.backend.service.name
            for rule in (ingress.spec.rules or [])
            for path in (rule.http.paths or [])
            if (path.backend.service.name, ingress_namespace) not in service_info
        ]
        non_existent_tls_secrets = [
            tls.secret_name
            for tls in (ingress.spec.tls or [])
            if (tls.secret_name, ingress_namespace) not in secrets_info
        ]
        conditions = [
            (
                ingress_class_name not in ingress_class_info,
                f"Ingress {ingress_namespace}/{ingress_name} uses "
                f"non-existent ingress class {ingress_class_name}.",
            ),
            (
                all(
                    [
                        hasattr(ingress, "spec"),
                        hasattr(ingress.spec, "rules"),
                        any(non_existent_services),
                    ]
                ),
                (
                    f"Ingress {ingress_namespace}/{ingress_name} uses "
                    f"non-existent service {', '.join(non_existent_services)}"
                    if non_existent_services
                    else ""
                ),
            ),
            (
                all(
                    [
                        hasattr(ingress, "spec"),
                        hasattr(ingress.spec, "tls"),
                        any(non_existent_tls_secrets),
                    ]
                ),
                (
                    f"Ingress {ingress_namespace}/{ingress_name} uses "
                    f"non-existent TLS secret {', '.join(non_existent_tls_secrets)}"
                    if non_existent_tls_secrets
                    else ""
                ),
            ),
        ]

        for condition, message in conditions:
            if condition:
                report.status_extended = message
                return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        services = data.get_services()
        secrets = data.get_secrets()
        ingress_classes = data.get_ingress_classes()

        for ingress in data.get_ingresses():
            report = CheckReportK8s(self.metadata())
            report.resource_id = ingress.metadata.uid
            report.resource_name = ingress.metadata.name
            report.resource_namespace = ingress.metadata.namespace
            report.status = "PASS"

            if not self._execute(ingress, services, secrets, ingress_classes, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
