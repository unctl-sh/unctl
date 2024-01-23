from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pod_crashloopbackoff(Check):
    def __init__(self, **data):
        super().__init__(**data)
        # load the schema for the check's metadata

    # TBD: tech debt
    def create_jobs(self):
        return None

    def _execute(self, pod, report) -> bool:
        container_statuses = pod.status.container_statuses or []

        # Check each container status within the pod
        for container_status in container_statuses:
            # Check if the container's last state is terminated
            # and the reason is 'CrashLoopBackOff'
            if (container_status.state.waiting) and (
                container_status.state.waiting.reason == "CrashLoopBackOff"
            ):
                # Set the resource_container attribute
                # to the current container's name
                report.resource_container = container_status.name
                report.status_extended = (
                    f"Container {container_status.name} in pod "
                    f"{pod.metadata.name} is in "
                    f"CrashLoopBackOff state."
                )
                return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        # Iterate over each pod
        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_pod = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace
            report.status = "PASS"

            if not self._execute(pod, report):
                report.status = "FAIL"
                report.status_extended = (
                    f"Pod {pod.metadata.name} in namespace {pod.metadata.namespace} "
                    f"has a container in CrashLoopBackOff state."
                )

            findings.append(report)

        return findings
