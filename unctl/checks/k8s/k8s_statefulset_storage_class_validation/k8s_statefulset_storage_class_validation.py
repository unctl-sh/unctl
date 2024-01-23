from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_statefulset_storage_class_validation(Check):
    def _execute(self, statefulset, storageClasses, report) -> bool:
        statefulset_namespace = statefulset.metadata.namespace
        statefulset_name = statefulset.metadata.name

        storage_class = [s.metadata.name for s in storageClasses]

        if statefulset.spec is None or statefulset.spec.volume_claim_templates is None:
            return True

        claims_list = statefulset.spec.volume_claim_templates
        for volume_claim_template in claims_list:
            storageclass_name = volume_claim_template.spec.storage_class_name
            # check if its valid name
            if storageclass_name is None or storageclass_name in storage_class:
                continue

            # bailing out on the first error
            report.resource_storageclass = storageclass_name
            report.status_extended = (
                f"StatefulSet {statefulset_name} uses non-existent storage_class "
                f"{storageclass_name} in namespace {statefulset_namespace}"
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        storageClasses = data.get_storage_classes()
        for statefulset in data.get_statefulsets():
            report = CheckReportK8s(self.metadata())
            report.resource_id = statefulset.metadata.uid
            report.resource_name = statefulset.metadata.name
            report.resource_namespace = statefulset.metadata.namespace
            report.status = "PASS"

            if not self._execute(statefulset, storageClasses, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
