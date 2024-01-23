from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_daemonset_pod_template_validation(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def execute(self, data) -> list[CheckReportK8s]:
        """
        Verifies if each container in the DaemonSet has both
        CPU and memory limits set and that they meet the specified
        minimum requirements (`100m` for CPU and `100Mi` for memory).
        """
        findings = []
        daemonsets = data.get_daemonsets()
        for ds in daemonsets:
            report = CheckReportK8s(self.metadata())
            report.resource_id = ds.metadata.uid
            report.resource_name = ds.metadata.name
            report.resource_namespace = ds.metadata.namespace

            for container in ds.spec.template.spec.containers:
                mem_limit = None
                cpu_limit = None

                # Check if resources and limits are set for the container
                if container.resources and container.resources.limits:
                    mem_limit = container.resources.limits.get("memory")
                    cpu_limit = container.resources.limits.get("cpu")

                # Check memory limit
                if not mem_limit or not self.is_memory_sufficient(mem_limit):
                    report.status = "FAIL"
                    report.status_extended = (
                        f"Memory limit for container '{container.name}'"
                        "is less than 100Mi"
                    )
                    break
                else:
                    report.status = "PASS"
                    report.status_extended = (
                        f"Memory limit for container '{container.name}'" " is adequate."
                    )

                # Check CPU limit
                if not cpu_limit or not self.is_cpu_sufficient(cpu_limit):
                    report.status = "FAIL"
                    report.status_extended += (
                        f" CPU limit for container '{container.name}'"
                        " is less than 100m"
                    )
                    break
                else:
                    report.status = "PASS"
                    report.status_extended += (
                        f" CPU limit for container '{container.name}'" " is adequate."
                    )
            findings.append(report)
        return findings

    @staticmethod
    def is_memory_sufficient(mem_limit: str) -> bool:
        """
        Check if memory is at least 100Mi.
        """
        if mem_limit.endswith("Mi"):
            return int(mem_limit[:-2]) >= 100
        elif mem_limit.endswith("Gi"):
            return int(mem_limit[:-2]) * 1024 >= 100  # Convert Gi to Mi
        return False

    @staticmethod
    def is_cpu_sufficient(cpu_limit: str) -> bool:
        """
        Check if CPU is at least 100m.
        """
        if cpu_limit.endswith("m"):
            return int(cpu_limit[:-1]) >= 100
        elif cpu_limit.isdigit():
            return int(cpu_limit) * 1000 >= 100  # Convert CPU cores to millicores
        return False
