import asyncio
import contextlib
import inspect

import aiomysql
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client import (
    AppsV1Api,
    AutoscalingV1Api,
    NetworkingV1Api,
    BatchV1Api,
    StorageV1Api,
)
from kubernetes_asyncio.client.api_client import ApiClient
from kubernetes_asyncio.client.rest import ApiException

from unctl.constants import CheckProviders
from unctl.lib.checks.check import Check
from unctl.lib.checks.check_report import CheckReport


# Data Collection Module


class DataCollector:
    _COLLECTORS = {}

    async def fetch_data(self):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        cls._COLLECTORS[kwargs["name"]] = cls

    @classmethod
    def make_collector(cls, name, *args, **kwargs):
        return cls._COLLECTORS[name](*args, **kwargs)


class KubernetesData:
    # keep parameters sorted alphabetically to avoid merge conflicts
    def __init__(
        self,
        configmaps,
        cronjobs,
        daemonsets,
        deployments,
        endpoints,
        hpas,
        ingress_classes,
        ingresses,
        nodes,
        pods,
        network_policies,
        pvcs,
        replicationControllers,
        replicaSets,
        secrets,
        services,
        statefulsets,
        storageClasses,
        events,
    ):
        self._configmaps = configmaps
        self._cronjobs = cronjobs
        self._daemonsets = daemonsets
        self._deployments = deployments
        self._endpoints = endpoints
        self._hpas = hpas
        self._ingress_classes = ingress_classes
        self._ingresses = ingresses
        self._nodes = nodes
        self._pods = pods
        self._network_policies = network_policies
        self._pvcs = pvcs
        self._replicationControllers = replicationControllers
        self._replicaSets = replicaSets
        self._secrets = secrets
        self._services = services
        self._statefulsets = statefulsets
        self._storageClasses = storageClasses
        self._events = events

    def get_configmaps(self):
        return self._configmaps

    def get_cronjobs(self):
        return self._cronjobs

    def get_daemonsets(self):
        return self._daemonsets

    def get_deployments(self):
        return self._deployments

    def get_endpoints(self):
        return self._endpoints

    def get_hpas(self):
        return self._hpas

    def get_ingress_classes(self):
        return self._ingress_classes

    def get_ingresses(self):
        return self._ingresses

    def get_nodes(self):
        return self._nodes

    def get_pods(self):
        return self._pods

    def get_network_policies(self):
        return self._network_policies

    def get_pvcs(self):
        return self._pvcs

    def get_replication_controllers(self):
        return self._replicationControllers

    def get_replica_sets(self):
        return self._replicaSets

    def get_secrets(self):
        return self._secrets

    def get_services(self):
        return self._services

    def get_statefulsets(self):
        return self._statefulsets

    def get_storage_classes(self):
        return self._storageClasses

    def get_events(self):
        return self._events


class MySQLData:
    def __init__(self, default_config_file):
        self._connection = None
        self.default_config_file = default_config_file

    async def get_dbname(self):
        # should be considered as a check namespace
        return (await self._get_connection())._db  # noqa

    async def get_max_connections(self):
        target = "max_connections"
        async with self._get_cursor() as cursor:
            await cursor.execute(f"SHOW VARIABLES LIKE '{target}';")
            result = await cursor.fetchone()
        return int(result[-1])

    async def get_connections_used(self):
        target = "Max_used_connections"
        async with self._get_cursor() as cursor:
            await cursor.execute(f"SHOW STATUS LIKE '{target}';")
            result = await cursor.fetchone()
        return int(result[-1])

    async def _get_connection(self):
        if self._connection is None:
            self._connection = await aiomysql.connect(
                read_default_file=self.default_config_file
            )
        return self._connection

    @contextlib.asynccontextmanager
    async def _get_cursor(self):
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            yield cursor


class MySQLDataCollector(DataCollector, name=CheckProviders.MySQL):
    DEFAULT_CONFIG_FILE = "~/.my.cnf"

    async def fetch_data(self):
        return MySQLData(self.DEFAULT_CONFIG_FILE)


class KubernetesDataCollector(DataCollector, name=CheckProviders.K8S):
    async def fetch_data(self):
        async def _fetch_items(awaitable):
            return (await awaitable).items

        # Load kube config
        await config.load_kube_config()

        try:
            async with ApiClient() as api:
                # Get an instance of the API class
                v1 = client.CoreV1Api(api)
                v1apps = AppsV1Api(api)
                v1autoscaling = AutoscalingV1Api(api)
                v1networking = NetworkingV1Api(api)
                v1storage = StorageV1Api(api)
                v1batch = BatchV1Api(api)

                hpas = _fetch_items(
                    v1autoscaling.list_horizontal_pod_autoscaler_for_all_namespaces()
                )

                tasks = {
                    "configmaps": _fetch_items(v1.list_config_map_for_all_namespaces()),
                    "cronjobs": _fetch_items(
                        v1batch.list_cron_job_for_all_namespaces()
                    ),
                    "daemonsets": _fetch_items(
                        v1apps.list_daemon_set_for_all_namespaces()
                    ),
                    "deployments": _fetch_items(
                        v1apps.list_deployment_for_all_namespaces()
                    ),
                    "endpoints": _fetch_items(v1.list_endpoints_for_all_namespaces()),
                    "hpas": hpas,
                    "ingress_classes": _fetch_items(v1networking.list_ingress_class()),
                    "ingresses": _fetch_items(
                        v1networking.list_ingress_for_all_namespaces()
                    ),
                    "network_policies": _fetch_items(
                        v1networking.list_network_policy_for_all_namespaces()
                    ),
                    "nodes": _fetch_items(v1.list_node(watch=False)),
                    "pods": _fetch_items(v1.list_pod_for_all_namespaces()),
                    "pvcs": _fetch_items(
                        v1.list_persistent_volume_claim_for_all_namespaces()
                    ),
                    "replicationControllers": _fetch_items(
                        v1.list_replication_controller_for_all_namespaces()
                    ),
                    "replicaSets": _fetch_items(
                        v1apps.list_replica_set_for_all_namespaces()
                    ),
                    "secrets": _fetch_items(v1.list_secret_for_all_namespaces()),
                    "services": _fetch_items(v1.list_service_for_all_namespaces()),
                    "statefulsets": _fetch_items(
                        v1apps.list_stateful_set_for_all_namespaces()
                    ),
                    "storageClasses": _fetch_items(v1storage.list_storage_class()),
                    "events": _fetch_items(v1.list_event_for_all_namespaces()),
                }
                results = dict(zip(tasks, await asyncio.gather(*tasks.values())))
                return KubernetesData(**results)

        except ApiException as api_exception:
            # Handle exceptions raised by Kubernetes API interactions
            print(f"An error occurred with the Kubernetes API: {api_exception.reason}")
            # print(api_exception.body)
            return None

        except Exception as general_exception:
            # A generic handler for all other exceptions
            print(f"An unexpected error occurred: {general_exception}")
            return None


# Main Application


class ResourceChecker:
    _check_reports: dict[str, list[CheckReport]]

    def __init__(
        self,
        display,
        collector: DataCollector,
        checks: list[Check],
        provider: str,
    ):
        self.display = display
        self._collector = collector
        self._checks = checks
        self._provider = provider
        self._check_reports = {}

    async def execute(self):
        data = await self._collector.fetch_data()
        if data is None:
            print("Failed to collect inventory")
            exit(1)

        total_checks = len(self._checks)

        completed_checks = 0

        # Display the progress bar header
        self.display.display_progress_bar_header()

        for check in self._checks:
            if check.Enabled is False:
                continue
            check_reports = (
                await check.execute(data)
                if inspect.iscoroutinefunction(check.execute)
                else check.execute(data)
            )
            self._check_reports[check.__class__.__name__] = check_reports
            completed_checks += 1
            self.display.display_progress_bar(
                completed_checks / total_checks, check.CheckTitle
            )

            print()  # New line after the progress bar completion

        return self._check_reports

    @property
    def failing_reports(self) -> list[CheckReport]:
        failing = []
        for check_list in self._check_reports.values():
            failing.extend(item for item in check_list if not item.passed)

        return failing

    @property
    def failing_objects(self):
        items = self.failing_reports
        objects = list(set(item.unique_name for item in items))
        return objects

    @property
    def reports(self):
        return self._check_reports


class JobDefinition:
    def __init__(self, check_modules):
        self.check_modules = check_modules

    def generate_jobs(self, suite_name=None):
        # TBD: this list should be generated based on the JSON file
        # Loads checks related to the suite specified
        # suite_path = os.path.join(self.checks_dir, suite_name)
        check_modules = self.check_modules

        jobs: list[Check] = []
        for module in check_modules:
            # Load only the checks
            if len(module.__package__.split(".")) < 4:
                continue

            # Extract class name from the module's file name
            class_name = module.__package__.split(".")[-1]

            # Instantiate the class named after the module
            check_class = getattr(module, class_name)

            # load the class
            check_instance = check_class()

            # Ensure that the execute method exists in the check class
            if hasattr(check_instance, "execute"):
                jobs.append(check_instance)

        return jobs
