import pytest
from kubernetes.client import (
    V1ObjectMeta,
    V1Deployment,
    V1DeploymentSpec,
    V1PodTemplateSpec,
    V1PodSpec,
    V1LabelSelector,
    V1Container,
    V1HorizontalPodAutoscaler,
    V1HorizontalPodAutoscalerSpec,
    V1CrossVersionObjectReference,
    V1ReplicationController,
    V1ReplicationControllerSpec,
    V1ReplicaSet,
    V1ReplicaSetSpec,
    V1ResourceRequirements,
    V1StatefulSet,
    V1StatefulSetSpec,
)

from test_utils.utils import _common_checks_test


# Horizontal pod autoscaling
@pytest.mark.parametrize(
    [
        "hpa_name",
        "hpa_namespace",
        "resource_name",
        "resource_namespace",
        "scale_target_ref_name",
        "scale_target_ref_kind",
        "requests",
        "limits",
    ],
    [
        # scale_target_ref_name matches but resource_namespace
        # does not match with hpa_namespace
        (
            "test_hpa",
            "test_ns1",
            "test_resource",
            "test_ns2",
            "test_resource",
            "Deployment",
            {"cpu": "100m", "memory": "256Mi"},
            {"cpu": "500m", "memory": "1Gi"},
        ),
        # resource_namespace matches but resource_name
        # does not match with scale_target_ref_name
        (
            "test_hpa",
            "test_ns",
            "test_resource1",
            "test_ns",
            "test_resource2",
            "Deployment",
            {"cpu": "100m", "memory": "256Mi"},
            {"cpu": "500m", "memory": "1Gi"},
        ),
        # scale_target_kind none of
        # Deployment, ReplicationController, ReplicaSet, Statefulset
        (
            "test_hpa",
            "test_ns",
            "test_resource",
            "test_ns",
            "test_resource",
            "test",
            {"cpu": "100m", "memory": "256Mi"},
            {"cpu": "500m", "memory": "1Gi"},
        ),
        # requests and limits values are None in a resource
        (
            "test_hpa",
            "test_ns",
            "test_resource",
            "test_ns",
            "test_resource",
            "Deployment",
            None,
            None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_horizontal_pod_autoscaling_negative(
    harness,
    capsys,
    hpa_name,
    hpa_namespace,
    resource_name,
    resource_namespace,
    scale_target_ref_name,
    scale_target_ref_kind,
    requests,
    limits,
):
    check_name = "k8s_horizontal_pod_autoscaling"

    # Creating a hpa object
    hpa = V1HorizontalPodAutoscaler(
        kind="HorizontalPodAutoscaler",
        metadata=V1ObjectMeta(name=hpa_name, namespace=hpa_namespace),
        spec=V1HorizontalPodAutoscalerSpec(
            scale_target_ref=V1CrossVersionObjectReference(
                name=scale_target_ref_name,
                kind=scale_target_ref_kind,
            ),
            min_replicas=1,
            max_replicas=2,
        ),
    )

    # Creating a deployment object
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1DeploymentSpec(
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a replication_controller object
    replication_controller = V1ReplicationController(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1ReplicationControllerSpec(
            selector={"app": "label"},
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a replicaset object
    replicaset = V1ReplicaSet(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1ReplicaSetSpec(
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a statefulset object
    statefulset = V1StatefulSet(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1StatefulSetSpec(
            service_name="test_service",
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                ),
            ),
        ),
    )

    harness.k8s_cluster.add_hpas(hpa)
    harness.k8s_cluster.add_deployments(deployment)
    harness.k8s_cluster.add_replication_controllers(replication_controller)
    harness.k8s_cluster.add_replicasets(replicaset)
    harness.k8s_cluster.add_statefulsets(statefulset)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=hpa_namespace,
        name=hpa_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_horizontal_pod_autoscaling_positive(harness, capsys):
    check_name = "k8s_horizontal_pod_autoscaling"

    (
        hpa_name,
        hpa_namespace,
        resource_name,
        resource_namespace,
        scale_target_ref_name,
        scale_target_ref_kind,
        requests,
        limits,
    ) = (
        "test_hpa",
        "test_ns",
        "test_resource",
        "test_ns",
        "test_resource",
        "Deployment",
        {"cpu": "100m", "memory": "256Mi"},
        {"cpu": "500m", "memory": "1Gi"},
    )

    # Creating a hpa object
    hpa = V1HorizontalPodAutoscaler(
        kind="HorizontalPodAutoscaler",
        metadata=V1ObjectMeta(name=hpa_name, namespace=hpa_namespace),
        spec=V1HorizontalPodAutoscalerSpec(
            scale_target_ref=V1CrossVersionObjectReference(
                name=scale_target_ref_name,
                kind=scale_target_ref_kind,
            ),
            min_replicas=1,
            max_replicas=2,
        ),
    )

    # Creating a deployment object
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1DeploymentSpec(
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a replication_controller object
    replication_controller = V1ReplicationController(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1ReplicationControllerSpec(
            selector={"app": "label"},
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a replicaset object
    replicaset = V1ReplicaSet(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1ReplicaSetSpec(
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                )
            ),
        ),
    )

    # Creating a statefulset object
    statefulset = V1StatefulSet(
        metadata=V1ObjectMeta(name=resource_name, namespace=resource_namespace),
        spec=V1StatefulSetSpec(
            service_name="test_service",
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            resources=V1ResourceRequirements(
                                requests=requests,
                                limits=limits,
                            ),
                        )
                    ]
                ),
            ),
        ),
    )

    harness.k8s_cluster.add_hpas(hpa)
    harness.k8s_cluster.add_deployments(deployment)
    harness.k8s_cluster.add_replication_controllers(replication_controller)
    harness.k8s_cluster.add_replicasets(replicaset)
    harness.k8s_cluster.add_statefulsets(statefulset)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=hpa_namespace,
            name=hpa_name,
            stdout=stdout,
            check_status="PASS",
        )
