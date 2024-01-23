import contextlib
from dataclasses import dataclass

from test_utils.networking.data_sources.base import BaseDataSource
from test_utils.networking.data_sources.k8s import K8SCluster
from test_utils.networking.interceptors import (
    K8SApiUrlInterceptor,
    BaseInterceptor,
)
from unctl.__main__ import process
from unctl.constants import CheckProviders
from unctl.lib.checks.loader import ChecksLoader
from unctl.lib.display.display import Displays
from unctl.scanrkube import JobDefinition, KubernetesDataCollector, ResourceChecker


@dataclass
class BaseTestingDatasource:
    data: BaseDataSource
    interceptor: BaseInterceptor

    @contextlib.contextmanager
    def spin_up(self):
        with self.interceptor.intercept():
            yield


@dataclass
class BaseProvider(BaseTestingDatasource):
    def run_check(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class TestingK8SCLuster(BaseProvider):
    async def run_check(self, check_id, *, display=None):
        collector = KubernetesDataCollector()
        display = display or Displays.get_display(CheckProviders.K8S)

        check = self.get_check(check_id)
        app = ResourceChecker(display, collector, [check], CheckProviders.K8S)

        return await app.execute()

    def get_checks(self, *check_ids):
        loader = ChecksLoader()
        check_modules = loader.load_all(provider="k8s", checks=check_ids)
        job_definer = JobDefinition(check_modules)
        jobs = job_definer.generate_jobs()
        return jobs

    def get_check(self, check_id):
        try:
            return self.get_checks(check_id)[0]
        except IndexError:
            raise LookupError(f"Check: {check_id} not found") from None

    def add_configmaps(self, *configmaps):
        self.data.configmaps.items.extend(configmaps)

    def add_deployments(self, *deployments):
        self.data.deployments.items.extend(deployments)

    def add_services(self, *services):
        self.data.services.items.extend(services)

    def add_cronjobs(self, *cronjobs):
        self.data.cronjobs.items.extend(cronjobs)

    def add_network_policies(self, *network_policies):
        self.data.network_policies.items.extend(network_policies)

    def add_pods(self, *pods):
        self.data.pods.items.extend(pods)

    def add_secrets(self, *secrets):
        self.data.secrets.items.extend(secrets)

    def add_daemonsets(self, *daemonsets):
        self.data.daemonsets.items.extend(daemonsets)

    def add_hpas(self, *hpas):
        self.data.hpas.items.extend(hpas)

    def add_replication_controllers(self, *replication_controllers):
        self.data.replication_controllers.items.extend(replication_controllers)

    def add_replicasets(self, *replicasets):
        self.data.replicasets.items.extend(replicasets)

    def add_statefulsets(self, *statefulsets):
        self.data.statefulsets.items.extend(statefulsets)

    def add_ingresses(self, *ingresses):
        self.data.ingresses.items.extend(ingresses)

    def add_ingressclasses(self, *ingressclasses):
        self.data.ingressclasses.items.extend(ingressclasses)

    def add_nodes(self, *nodes):
        self.data.nodes.items.extend(nodes)

    def add_endpoints(self, *endpoints):
        self.data.endpoints.items.extend(endpoints)

    def add_pvcs(self, *pvcs):
        self.data.pvcs.items.extend(pvcs)

    def add_storage_classes(self, *storageclasses):
        self.data.storageclasses.items.extend(storageclasses)

    def add_events(self, *events):
        self.data.events.items.extend(events)


class Harness:
    """
    Serves as a main tests utility that's being shared across all the tests.
    Any common test logic or any abstraction that makes the testing process
    easier should be added here.
    """

    def __init__(self, k8s_cluster: TestingK8SCLuster):
        self.k8s_cluster = k8s_cluster

    @classmethod
    def create(cls):
        return cls(cls.setup_k8s_cluster())

    @contextlib.contextmanager
    def spin_up(self):
        with self.k8s_cluster.spin_up():
            yield

    @classmethod
    def setup_k8s_cluster(cls, cluster=None):
        """
        Can be used to operate with multiple clusters ot once.

        All clusters will be called in the correct order (from the newest to the oldest)
        depending
            on matching API URLs, E.g:
            >>> with harness.k8s_cluster.spin_up(
            ):  # has interceptor for /configmaps URL
            >>>     new_cluster = harness.setup_k8s_cluster(
                    ...
                    )  # has interceptor for /cronjob URL
            >>>     with new_cluster.spin_up():
            >>>         pass
            If we send a request to /configmaps, it'll go to `new_cluster` first,
            it'll be unable to find the interceptor for that URL,
            so it'll proceed to an oldest cluster,
            which has the interceptor for that URL.
            That way you can chain as many clusters as you want to, for example,
            partially test clusters within the same check.
        """
        cluster = cluster or K8SCluster()
        interceptor = K8SApiUrlInterceptor.create_interceptor_for(cluster)
        return TestingK8SCLuster(cluster, interceptor)

    def run_unctl(self, options):
        return process(options)
