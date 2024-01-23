from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pod_high_restart_count(Check):
    # def _execute(self, pod, report) -> bool:
    #     # Get the current time
    #     now = datetime.now()

    #     # Define the time window for restart checks (last 30 minutes)
    #     time_window = now - timedelta(minutes=30)
    #     for container_status in pod.status.container_statuses:
    #         # Check if the restart count is greater than 10
    #         if container_status.restart_count > 10:
    #             # Get events related to the pod
    #             field_selector = f"involvedObject.name={pod.metadata.name}"
    #             events = v1.list_namespaced_event(
    #                 namespace=pod.metadata.namespace,
    #                 field_selector=field_selector).items
    #             # Check if there are recent restart events
    #             # recent_restart_events = [
    #               event for event in events
    #               if "Restarted" in event.reason
    #               and event.last_timestamp >= time_window
    #             ]
    #             # Report if recent restart events are found
    #             if recent_restart_events:
    #                 print(
    #                   f"Pod {pod.metadata.name} in namespace "
    #                   f"{pod.metadata.namespace} has restarted "
    #                   f"more than 10 times in the last 30 minutes!"
    #                   )

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_pod = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace

            container_statuses = (
                pod.status.container_statuses if pod.status.container_statuses else []
            )

            # Identify containers with high restart counts
            high_restart_containers = [
                container_status.name
                for container_status in container_statuses
                if container_status and container_status.restart_count > 10
            ]

            if high_restart_containers:
                report.status = "FAIL"
                report.status_extended = (
                    f"Containers {', '.join(high_restart_containers)} "
                    "in the pod have restarted more than 10 times."
                )
                # Assuming multiple containers can have high restarts,
                # store them all.
                report.resource_container = ", ".join(high_restart_containers)
            else:
                report.status = "PASS"
                report.status_extended = (
                    "Pod's containers are within acceptable restart limits."
                )

            findings.append(report)

        return findings
