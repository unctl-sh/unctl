from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_daemonset_configmap_existence(Check):
    def _execute(self, daemonset, configmaps, report) -> bool:
        configmap_names = [
            (configmap.metadata.name, configmap.metadata.namespace)
            for configmap in configmaps
        ]
        daemonset_namespace = daemonset.metadata.namespace

        if daemonset.spec.template.spec.volumes:
            for volume in daemonset.spec.template.spec.volumes:
                if volume.config_map is not None:
                    daemonset_configmap_name = volume.config_map.name
                    configmap_match_found = False
                    for configmap_name, configmap_namespace in configmap_names:
                        if configmap_name == daemonset_configmap_name and (
                            configmap_namespace == daemonset_namespace
                        ):
                            configmap_match_found = True
                            break
                    if configmap_match_found is False:
                        report.status_extended = (
                            f"ConfigMap name {volume.config_map.name}"
                            "in Daemonset for namespace "
                            f"{daemonset.metadata.namespace} does not exist "
                            "in the list of ConfigMaps."
                        )
                        report.resource_configmap = daemonset_configmap_name
                        return False
        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        configmaps = data.get_configmaps()

        for daemonset in data.get_daemonsets():
            report = CheckReportK8s(self.metadata())
            report.resource_id = daemonset.metadata.uid
            report.resource_name = daemonset.metadata.name
            report.resource_namespace = daemonset.metadata.namespace
            report.status = "PASS"

            if not self._execute(daemonset, configmaps, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
