from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_insufficient_pids_on_node(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []
        pid_threshold = 100  # Define a threshold for PIDs

        for node in data.get_nodes():
            report = CheckReportK8s(self.metadata())
            report.resource_id = node.metadata.uid
            report.resource_name = node.metadata.name
            report.resource_node = node.metadata.name

            allocatable_pids = int(node.status.allocatable.get("pids", 0))
            if allocatable_pids > 0:
                if allocatable_pids < pid_threshold:
                    report.status = "FAIL"
                    report.status_extended = (
                        f"Node {node.metadata.name} has only {allocatable_pids}"
                        " allocatable PIDs, "
                        f"which is below the threshold of {pid_threshold} PIDs."
                    )
                else:
                    report.status = "PASS"
                    report.status_extended = f"Node {node.metadata.name} has sufficient"
                    " number of allocatable PIDs."
            else:
                report.status = "FAIL"
                report.status_extended = "PID metrics for the node are not available."

            findings.append(report)

        return findings
