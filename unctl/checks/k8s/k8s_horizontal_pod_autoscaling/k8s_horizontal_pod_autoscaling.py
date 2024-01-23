from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_horizontal_pod_autoscaling(Check):
    def _execute(
        self,
        hpa,
        deployments,
        replication_controllers,
        replicasets,
        statefulsets,
        report,
    ) -> bool:
        scale_target_ref_name = hpa.spec.scale_target_ref.name
        hpa_namespace = hpa.metadata.namespace
        scale_target_kind = hpa.spec.scale_target_ref.kind

        resource_lookup = {
            "Deployment": deployments,
            "ReplicationController": replication_controllers,
            "ReplicaSet": replicasets,
            "StatefulSet": statefulsets,
        }

        matched_resource = None

        if scale_target_kind in resource_lookup:
            for resource in resource_lookup[scale_target_kind]:
                if (resource.metadata.name == scale_target_ref_name) and (
                    resource.metadata.namespace == hpa_namespace
                ):
                    matched_resource = resource
                    break
        else:
            report.status_extended = (
                f"HorizontalPodAutoscaler uses {scale_target_kind} as "
                f"ScaleTargetRef, which is not an option."
            )
            return False

        if matched_resource is None:
            report.status_extended = (
                f"HorizontalPodAutoscaler uses "
                f"{scale_target_kind}/{scale_target_ref_name} as "
                f"ScaleTargetRef, which does not exist."
            )
            return False

        report.resource_dep_type = hpa.spec.scale_target_ref.kind
        report.resource_dep_name = hpa.spec.scale_target_ref.name
        containers = len(matched_resource.spec.template.spec.containers)

        for container in matched_resource.spec.template.spec.containers:
            if (container.resources.requests is None) or (
                container.resources.limits is None
            ):
                containers -= 1

        if containers <= 0:
            report.status_extended = (
                f"{scale_target_kind} "
                f"{hpa.metadata.namespace}/{scale_target_ref_name} "
                f"does not have resource configured."
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        deployments = data.get_deployments()
        replication_controllers = data.get_replication_controllers()
        replicasets = data.get_replica_sets()
        statefulsets = data.get_statefulsets()

        for hpa in data.get_hpas():
            report = CheckReportK8s(self.metadata())
            report.resource_id = hpa.metadata.uid
            report.resource_name = hpa.metadata.name
            report.resource_namespace = hpa.metadata.namespace
            report.status = "PASS"

            if not self._execute(
                hpa,
                deployments,
                replication_controllers,
                replicasets,
                statefulsets,
                report,
            ):
                report.status = "FAIL"

            findings.append(report)

        return findings
