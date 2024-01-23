from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Type

from kubernetes.client import (
    V1ConfigMapList,
    V1DeploymentList,
    V1ServiceList,
    V1CronJobList,
    V1NetworkPolicyList,
    V1PodList,
    V1SecretList,
    V1DaemonSetList,
    V1PersistentVolumeClaimList,
    V1NodeList,
    V1HorizontalPodAutoscalerList,
    V1ReplicationControllerList,
    V1ReplicaSetList,
    V1StatefulSetList,
    V1IngressList,
    V1IngressClassList,
    V1EndpointsList,
    V1StorageClassList,
    CoreV1EventList,
)
from test_utils.networking.adapters import AIOHTTPAdapter, AIOHTTP_REQUEST_SPEC
from test_utils.networking.data_sources.base import BaseDataSource
from test_utils.networking.data_sources.decorators import http_intercepts


@dataclass
class K8SCluster(BaseDataSource):
    configmaps: V1ConfigMapList = field(
        default_factory=lambda: V1ConfigMapList(items=[])
    )
    deployments: V1DeploymentList = field(
        default_factory=lambda: V1DeploymentList(items=[])
    )
    services: V1ServiceList = field(default_factory=lambda: V1ServiceList(items=[]))
    cronjobs: V1CronJobList = field(default_factory=lambda: V1CronJobList(items=[]))
    network_policies: V1NetworkPolicyList = field(
        default_factory=lambda: V1NetworkPolicyList(items=[])
    )
    pods: V1PodList = field(default_factory=lambda: V1PodList(items=[]))
    secrets: V1SecretList = field(default_factory=lambda: V1SecretList(items=[]))
    daemonsets: V1DaemonSetList = field(
        default_factory=lambda: V1DaemonSetList(items=[])
    )
    hpas: V1HorizontalPodAutoscalerList = field(
        default_factory=lambda: V1HorizontalPodAutoscalerList(items=[])
    )
    replication_controllers: V1ReplicationControllerList = field(
        default_factory=lambda: V1ReplicationControllerList(items=[])
    )
    replicasets: V1ReplicaSetList = field(
        default_factory=lambda: V1ReplicaSetList(items=[])
    )
    statefulsets: V1StatefulSetList = field(
        default_factory=lambda: V1StatefulSetList(items=[])
    )
    ingresses: V1IngressList = field(default_factory=lambda: V1IngressList(items=[]))
    ingressclasses: V1IngressClassList = field(
        default_factory=lambda: V1IngressClassList(items=[])
    )
    services: V1ServiceList = field(default_factory=lambda: V1ServiceList(items=[]))
    nodes: V1NodeList = field(default_factory=lambda: V1NodeList(items=[]))
    endpoints: V1EndpointsList = field(
        default_factory=lambda: V1EndpointsList(items=[])
    )
    pvcs: V1PersistentVolumeClaimList = field(
        default_factory=lambda: V1PersistentVolumeClaimList(items=[])
    )
    storageclasses: V1StorageClassList = field(
        default_factory=lambda: V1StorageClassList(items=[])
    )
    events: CoreV1EventList = field(default_factory=lambda: CoreV1EventList(items=[]))

    def _response(
        self,
        data,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        status=HTTPStatus.OK,
        headers=None,
    ):
        return response_type(
            status=status, response_data=data, reason=None, headers=headers or {}
        )

    @http_intercepts("GET", "configmaps")
    def get_configmaps(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.configmaps.to_dict(), response_type)

    @http_intercepts("GET", "deployments")
    def get_deployments(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.deployments.to_dict(), response_type)

    @http_intercepts("GET", "services")
    def get_services(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.services.to_dict(), response_type)

    @http_intercepts("GET", "cronjobs")
    def get_cronjobs(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.cronjobs.to_dict(), response_type)

    @http_intercepts("GET", "networkpolicies")
    def get_network_policies(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.network_policies.to_dict(), response_type)

    @http_intercepts("GET", "pods")
    def get_pods(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.pods.to_dict(), response_type)

    @http_intercepts("GET", "secrets")
    def get_secrets(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.secrets.to_dict(), response_type)

    @http_intercepts("GET", "daemonsets")
    def get_daemonsets(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.daemonsets.to_dict(), response_type)

    @http_intercepts("GET", "horizontalpodautoscalers")
    def get_hpas(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.hpas.to_dict(), response_type)

    @http_intercepts("GET", "replicationcontrollers")
    def get_replicationControllers(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.replication_controllers.to_dict(), response_type)

    @http_intercepts("GET", "replicasets")
    def get_replicasets(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.replicasets.to_dict(), response_type)

    @http_intercepts("GET", "statefulsets")
    def get_statefulsets(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.statefulsets.to_dict(), response_type)

    @http_intercepts("GET", "ingresses")
    def get_ingresses(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.ingresses.to_dict(), response_type)

    @http_intercepts("GET", "ingressclasses")
    def get_ingressclasses(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.ingressclasses.to_dict(), response_type)

    @http_intercepts("GET", "nodes?watch=False")
    def get_nodes(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.nodes.to_dict(), response_type)

    @http_intercepts("GET", "endpoints")
    def get_endpoints(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.endpoints.to_dict(), response_type)

    @http_intercepts("GET", "persistentvolumeclaims")
    def get_pvcs(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.pvcs.to_dict(), response_type)

    @http_intercepts("GET", "storageclasses")
    def get_storage_classes(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.storageclasses.to_dict(), response_type)

    @http_intercepts("GET", "events")
    def get_events(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
        context,
    ):
        return self._response(self.events.to_dict(), response_type)

    # if no interceptor found, use default
    def __interceptor_missing__(
        self,
        request: AIOHTTP_REQUEST_SPEC,
        response_type: Type[AIOHTTPAdapter.RESPONSE_TYPE],
    ):
        return self._response({"items": []}, response_type)
