from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_node_out_of_memory(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []
        for node in data.get_nodes():
            report = CheckReportK8s(self.metadata())
            report.resource_id = node.metadata.name
            report.resource_name = node.metadata.name
            report.resource_node = node.metadata.name

            # Extract memory usage and capacity from node metrics
            allocatable_memory = node.status.allocatable.get("memory")
            capacity_memory = node.status.capacity.get("memory")

            if allocatable_memory and capacity_memory:
                allocatable_memory = self._convert_to_megabytes(allocatable_memory)
                capacity_memory = self._convert_to_megabytes(capacity_memory)
                memory_usage_percentage = (allocatable_memory / capacity_memory) * 100

                if memory_usage_percentage > 85:
                    report.status = "FAIL"
                    report.status_extended = (
                        f"Node is using {memory_usage_percentage:.2f}% "
                        "of its memory capacity, which is above the "
                        "threshold of 85%."
                    )
                else:
                    report.status = "PASS"
                    report.status_extended = (
                        "Node's memory usage is within acceptable limits."
                    )
            else:
                report.status = "FAIL"
                report.status_extended = (
                    "Memory metrics for the node are not available."
                )

            findings.append(report)

        return findings

    @staticmethod
    def _convert_to_megabytes(memory_string: str) -> int:
        units = {"Ki": 1 / 1024, "Mi": 1, "Gi": 1024, "Ti": 1024 * 1024}
        number, unit = int(memory_string[:-2]), memory_string[-2:]
        return number * units[unit]
