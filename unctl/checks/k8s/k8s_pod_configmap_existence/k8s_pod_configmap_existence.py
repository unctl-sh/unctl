from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pod_configmap_existence(Check):
    def _execute(self, pod, configmaps, report) -> bool:
        configmap_names = {
            (configmap.metadata.name, configmap.metadata.namespace)
            for configmap in configmaps
        }
        pod_namespace = pod.metadata.namespace

        for container in pod.spec.containers:
            if container.env:
                for env_var in container.env:
                    if all(
                        (
                            hasattr(env_var, "value_from"),
                            env_var.value_from is not None,
                            getattr(env_var.value_from, "config_map_key_ref", None)
                            is not None,
                        )
                    ):
                        configmap_name = env_var.value_from.config_map_key_ref.name
                        if (
                            configmap_name,
                            pod_namespace,
                        ) not in configmap_names:
                            report.resource_configmap = configmap_name
                            report.status_extended = (
                                f"ConfigMap name {configmap_name} in Pod "
                                f"for namespace {pod_namespace} does not "
                                "exist in the list of ConfigMaps."
                            )
                            return False

        for volume in pod.spec.volumes:
            if volume.config_map is not None:
                configmap_name = volume.config_map.name
                if (
                    configmap_name,
                    pod_namespace,
                ) not in configmap_names:
                    report.resource_configmap = configmap_name
                    report.status_extended = (
                        f"ConfigMap name {configmap_name} in Pod "
                        f"for namespace {pod_namespace} does not "
                        "exist in the list of ConfigMaps."
                    )
                    return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        configmaps = data.get_configmaps()
        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace
            report.status = "PASS"

            if not self._execute(pod, configmaps, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
