from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_node_ready(Check):
    def _execute(self, node, report) -> bool:
        failures = []

        for condition in node.status.conditions:
            # node is ready
            if condition.type == "Ready" and condition.status == "True":
                continue

            # node is not ready
            if condition.type == "Ready" and condition.status != "True":
                failures.append({"name": node.metadata.name, "condition": condition})

            # node has some other failure condition
            if condition.status != "False":
                failures.append({"name": node.metadata.name, "condition": condition})

        if len(failures) > 0:
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        for node in data.get_nodes():
            report = CheckReportK8s(self.metadata())
            report.resource_id = node.metadata.uid
            report.resource_name = node.metadata.name
            report.resource_node = node.metadata.name
            report.status = "PASS"

            if not self._execute(node, report):
                report.status = "FAIL"
                report.status_extended = "Node has failure conditions"

            findings.append(report)

        return findings
