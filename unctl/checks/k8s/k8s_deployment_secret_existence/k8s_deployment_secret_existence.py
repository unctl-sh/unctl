from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_deployment_secret_existence(Check):
    def _execute(self, deployment, secrets, report) -> bool:
        secretsInfo = [(s.metadata.name, s.metadata.namespace) for s in secrets]
        deployment_namespace = deployment.metadata.namespace

        containers_info = deployment.spec.template.spec.containers or []

        # Get the secrets from deployments
        secrets = [
            env.value_from.secret_key_ref.name
            for container_info in containers_info
            for env in (container_info.env or [])
            if env.value_from and env.value_from.secret_key_ref
        ]

        no_match_found = True

        for secret_name in secrets:
            if (secret_name, deployment_namespace) not in secretsInfo:
                report.status_extended = (
                    f"Secret name {secret_name} in Deployment for namespace "
                    f"{deployment_namespace} does not exist "
                    "in the list of Secrets."
                )

                no_match_found = False  # Set the flag to False

        return no_match_found

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        secrets = data.get_secrets()
        for deployment in data.get_deployments():
            report = CheckReportK8s(self.metadata())
            report.resource_id = deployment.metadata.uid
            report.resource_name = deployment.metadata.name
            report.resource_namespace = deployment.metadata.namespace
            report.status = "PASS"

            if not self._execute(deployment, secrets, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
