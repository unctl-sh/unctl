from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_excessive_pods_on_node(Check):
    def _execute(self, node, pod_count, report) -> bool:
        # Assume each pod requests these resources
        POD_REQUESTS = {"cpu": 50, "memory": 128 * 1024}  # 50m  # 128Ki

        cpu_capacity = 0
        mem_capacity = 0

        # Calculate capacity thresholds
        if node.status.allocatable["cpu"].endswith("m"):
            cpu_capacity = node.status.allocatable["cpu"].rstrip("m")
        elif node.status.allocatable["cpu"].endswith("0"):
            cpu_capacity = node.status.allocatable["cpu"]
        else:
            assert "Unexpected CPU capacity format"

        if node.status.allocatable["memory"].endswith("Ki"):
            mem_capacity = node.status.allocatable["memory"].rstrip("Ki")
        elif node.status.allocatable["memory"].endswith("Mi"):
            mem_capacity = node.status.allocatable["memory"].rstrip("Mi") + "000"
        else:
            assert "Unexpected memory capacity format"

        # Estimate max pods based on capacity / assumed pod requests
        max_cpu_pods = int(cpu_capacity) // POD_REQUESTS["cpu"]
        max_mem_pods = int(mem_capacity) // POD_REQUESTS["memory"]

        if pod_count > max_cpu_pods * 0.8:
            report.status_extended = (
                f"Node has too many pods ({pod_count}/{max_cpu_pods}) "
                f"by CPU {cpu_capacity}"
            )
            return False

        if pod_count > max_mem_pods * 0.8:
            report.status_extended = (
                f"Node has too many pods ({pod_count}/{max_mem_pods})"
                f" by memory {mem_capacity}"
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        node_pod_count = {}
        for pod in data.get_pods():
            node_name = pod.spec.node_name
            if node_name not in node_pod_count:
                node_pod_count[node_name] = 0
            node_pod_count[node_name] += 1

        for node in data.get_nodes():
            report = CheckReportK8s(self.metadata())
            report.resource_id = node.metadata.uid
            report.resource_name = node.metadata.name
            report.resource_node = node.metadata.name
            report.status = "PASS"

            if self._execute(node, node_pod_count[node.metadata.name], report) is False:
                report.status = "FAIL"

            findings.append(report)

        return findings
