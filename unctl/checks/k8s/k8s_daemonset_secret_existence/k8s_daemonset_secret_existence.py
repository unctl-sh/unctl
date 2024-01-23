from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_daemonset_secret_existence(Check):
    def _execute(self, daemonset, secrets, report) -> bool:
        secrets_info = {
            (secret.metadata.name, secret.metadata.namespace) for secret in secrets
        }
        daemonset_namespace = daemonset.metadata.namespace

        volumes = daemonset.spec.template.spec.volumes
        no_match_found = True

        if volumes is not None:
            for volume in volumes:
                if hasattr(volume, "secret") and hasattr(volume.secret, "secret_name"):
                    secret_name = volume.secret.secret_name
                    if not any(
                        secret_name == secret[0] and daemonset_namespace == secret[1]
                        for secret in secrets_info
                    ):
                        report.status_extended = (
                            f"Secret name {secret_name} in Daemonset "
                            f"for namespace {daemonset_namespace} does "
                            "not exist in the list of Secrets."
                        )

                        no_match_found = False
                        break  # Exit the loop when a mismatch is found

        return no_match_found

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        secrets = data.get_secrets()
        for daemonset in data.get_daemonsets():
            report = CheckReportK8s(self.metadata())
            report.resource_id = daemonset.metadata.uid
            report.resource_name = daemonset.metadata.name
            report.resource_namespace = daemonset.metadata.namespace
            report.status = "PASS"

            if not self._execute(daemonset, secrets, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
