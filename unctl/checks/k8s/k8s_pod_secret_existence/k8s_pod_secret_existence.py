from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pod_secret_existence(Check):
    def _execute(self, pod, secrets, report) -> bool:
        secrets_info = {
            (secret.metadata.name, secret.metadata.namespace) for secret in secrets
        }
        pod_namespace = pod.metadata.namespace
        pod_name = pod.metadata.name

        for container in pod.spec.containers:
            if container.env:
                for env_var in container.env:
                    if all(
                        (
                            hasattr(env_var, "value_from"),
                            env_var.value_from is not None,
                            getattr(env_var.value_from, "secret_key_ref", None)
                            is not None,
                        )
                    ):
                        secret_name = env_var.value_from.secret_key_ref.name
                        if (
                            secret_name,
                            pod_namespace,
                        ) not in secrets_info:
                            report.status_extended = (
                                f"Secret name {secret_name} in pod {pod_name} "
                                f"for namespace {pod_namespace} "
                                "does not exist in the list of Secrets."
                            )
                            return False
        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        secrets = data.get_secrets()
        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace
            report.status = "PASS"

            if not self._execute(pod, secrets, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
