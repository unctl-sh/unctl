from datetime import datetime
from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_daemonset_unused(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        daemonsets = data.get_daemonsets()
        pods = data.get_pods()

        # Get DaemonSet names which have pods associated with them.
        associated_daemonsets = set()
        for pod in pods:
            owner_references = pod.metadata.owner_references
            if owner_references:
                for owner in owner_references:
                    if owner.kind == "DaemonSet":
                        associated_daemonsets.add(owner.name)

        # Now, check all DaemonSets if they are not in associated_daemonsets.
        for ds in daemonsets:
            report = CheckReportK8s(self.metadata())
            report.resource_id = ds.metadata.uid
            report.resource_name = ds.metadata.name
            report.resource_namespace = ds.metadata.namespace

            if ds.metadata.name not in associated_daemonsets:
                # Check if the DaemonSet was created at least 30 days ago
                creation_time = ds.metadata.creation_timestamp
                time_delta = datetime.now(creation_time.tzinfo) - creation_time
                if time_delta.days > 30:
                    report.status = "FAIL"
                    report.status_extended = (
                        "DaemonSet has been unused for over 30 days."
                    )
                else:
                    report.status = "PASS"
                    report.status_extended = (
                        "DaemonSet is new and may not have had time to deploy pods yet."
                    )
            else:
                report.status = "PASS"
                report.status_extended = "DaemonSet is in use."

            findings.append(report)

        return findings
