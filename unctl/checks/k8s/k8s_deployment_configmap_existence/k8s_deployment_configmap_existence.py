from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_deployment_configmap_existence(Check):
    def _execute(self, deployment, configmaps, report) -> bool:
        configmap_names = [
            (configmap.metadata.name, configmap.metadata.namespace)
            for configmap in configmaps
        ]
        deployment_namespace = deployment.metadata.namespace

        if deployment.spec.template.spec.volumes:
            for volume in deployment.spec.template.spec.volumes:
                if volume.config_map is not None:
                    deployment_configmap_name = volume.config_map.name

                    configmap_match_found = False

                    for configmap_name, configmap_namespace in configmap_names:
                        if (configmap_name == deployment_configmap_name) and (
                            configmap_namespace == deployment_namespace
                        ):
                            configmap_match_found = True
                            break

                    if configmap_match_found is False:
                        report.status_extended = (
                            f"ConfigMap name {volume.config_map.name} in Deployment "
                            f"namespace {deployment.metadata.namespace} "
                            "does not exist in the list of ConfigMaps."
                        )
                        report.resource_configmap = deployment_configmap_name
                        return False
        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        configmaps = data.get_configmaps()
        for deployment in data.get_deployments():
            report = CheckReportK8s(self.metadata())
            report.resource_id = deployment.metadata.uid
            report.resource_name = deployment.metadata.name
            report.resource_namespace = deployment.metadata.namespace
            report.status = "PASS"

            if not self._execute(deployment, configmaps, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
