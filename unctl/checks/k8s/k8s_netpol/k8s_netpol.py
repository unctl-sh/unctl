from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_netpol(Check):
    def _execute(self, network_policy, pods, report) -> bool:
        if not network_policy.spec.pod_selector.match_labels:
            report.status_extended = (
                f"Network policy {network_policy.metadata.name} "
                "allows traffic to all pods"
            )
            return False

        else:
            filtered_pods = [
                pod
                for pod in pods
                if pod.metadata.labels
                if all(
                    label in pod.metadata.labels.items()
                    for label in network_policy.spec.pod_selector.match_labels.items()
                )
            ]
            if len(filtered_pods) == 0:
                report.status_extended = (
                    f"Network policy {network_policy.metadata.name} "
                    "is not applied to any pods"
                )
                return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        pods = data.get_pods()
        for network_policy in data.get_network_policies():
            report = CheckReportK8s(self.metadata())
            report.resource_id = network_policy.metadata.uid
            report.resource_name = network_policy.metadata.name
            report.resource_namespace = network_policy.metadata.namespace

            report.status = "PASS"

            if not self._execute(network_policy, pods, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
