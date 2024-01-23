from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_statefulset_service_validation(Check):
    def _execute(self, statefulset, services, report) -> bool:
        statefulset_service_name = statefulset.spec.service_name
        statefulset_namespace = statefulset.metadata.namespace
        statefulset_name = statefulset.metadata.name

        service_info = [(s.metadata.name, s.metadata.namespace) for s in services]
        match_found = False

        for name, namespace in service_info:
            # Check whether the name and namespace from service_info matches
            # name and namespace from the statefulset
            if name == statefulset_service_name and namespace == statefulset_namespace:
                match_found = True
                break
        if match_found is False:
            report.status_extended = (
                f"StatefulSet {statefulset_name} uses non-existent service "
                f"{statefulset_service_name} in namespace {statefulset_namespace}"
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        services = data.get_services()
        for statefulset in data.get_statefulsets():
            report = CheckReportK8s(self.metadata())
            report.resource_id = statefulset.metadata.uid
            report.resource_name = statefulset.metadata.name
            report.resource_namespace = statefulset.metadata.namespace
            report.status = "PASS"

            if not self._execute(statefulset, services, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
