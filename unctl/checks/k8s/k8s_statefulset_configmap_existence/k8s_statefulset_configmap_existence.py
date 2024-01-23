from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_statefulset_configmap_existence(Check):
    def _execute(self, statefulset, configmaps, report) -> bool:
        configmap_names = {
            (configmap.metadata.name, configmap.metadata.namespace)
            for configmap in configmaps
        }
        statefulset_namespace = statefulset.metadata.namespace

        # Check volume claim templates
        if statefulset.spec.volume_claim_templates is not None:
            for volume_claim_template in statefulset.spec.volume_claim_templates:
                if hasattr(volume_claim_template.spec, "data_source") and hasattr(
                    volume_claim_template.spec.data_source, "name"
                ):
                    configmap_vct = volume_claim_template.spec.data_source.name
                    if configmap_vct not in [
                        name
                        for (name, namespace) in configmap_names
                        if namespace == statefulset_namespace
                    ]:
                        report.status_extended = (
                            f"ConfigMap {configmap_vct} "
                            f"not found in namespace {statefulset_namespace}"
                        )
                        report.resource_configmap = configmap_vct
                        return False

        # Check volumes
        if statefulset.spec.template.spec.volumes is not None:
            for volume in statefulset.spec.template.spec.volumes:
                if hasattr(volume.config_map, "name") and volume.config_map.name:
                    configmap_vol = volume.config_map.name
                    if configmap_vol not in [
                        name
                        for (name, namespace) in configmap_names
                        if namespace == statefulset_namespace
                    ]:
                        report.status_extended = (
                            f"ConfigMap {configmap_vol} "
                            f"not found in namespace {statefulset_namespace}"
                        )
                        report.resource_configmap = configmap_vol
                        return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        configmaps = data.get_configmaps()
        for statefulset in data.get_statefulsets():
            report = CheckReportK8s(self.metadata())
            report.resource_id = statefulset.metadata.uid
            report.resource_name = statefulset.metadata.name
            report.resource_namespace = statefulset.metadata.namespace
            report.status = "PASS"

            if not self._execute(statefulset, configmaps, report):
                report.status = "FAIL"

            findings.append(report)
        return findings
