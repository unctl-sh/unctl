import pytest
from kubernetes.client import (
    V1StatefulSet,
    V1ObjectMeta,
    V1PodSpec,
    V1PersistentVolumeClaim,
    V1Volume,
    V1ConfigMapVolumeSource,
    V1ConfigMap,
    V1StatefulSetSpec,
    V1PodTemplateSpec,
    V1ResourceRequirements,
    V1LabelSelector,
    V1PersistentVolumeClaimSpec,
    V1TypedLocalObjectReference,
)

from test_utils.utils import _common_checks_test


# Statefulset configmap existence
@pytest.mark.parametrize(
    [
        "configmap_name",
        "configmap_namespace",
        "statefulset_configmap_name",
        "statefulset_name",
        "statefulset_namespace",
    ],
    [
        # configmap name matches but namespace does not match
        ("test", "test_ns1", "test", "test_statefulset", "test_ns2"),
        # namespace matches but configmap name does not match
        ("test1", "test_ns", "test2", "test_statefulset", "test_ns"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_statefulset_configmap_existence_negative(
    harness,
    capsys,
    configmap_name,
    configmap_namespace,
    statefulset_configmap_name,
    statefulset_name,
    statefulset_namespace,
):
    check_name = "k8s_statefulset_configmap_existence"

    # Create Configmap object
    config_map = V1ConfigMap(
        kind="ConfigMap",
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace),
    )

    # Create StatefulSet object
    statefulset = V1StatefulSet(
        kind="StatefulSet",
        metadata=V1ObjectMeta(name=statefulset_name, namespace=statefulset_namespace),
        spec=V1StatefulSetSpec(
            service_name="test_service",
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            config_map=V1ConfigMapVolumeSource(
                                name=statefulset_configmap_name
                            ),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                ),
            ),
            volume_claim_templates=[
                V1PersistentVolumeClaim(
                    metadata=V1ObjectMeta(name="data-volume"),
                    spec=V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources=V1ResourceRequirements(requests={"storage": "1Gi"}),
                        data_source=V1TypedLocalObjectReference(
                            name=statefulset_configmap_name, kind="PersistentVolume"
                        ),
                    ),
                )
            ],
        ),
    )

    harness.k8s_cluster.add_statefulsets(statefulset)
    harness.k8s_cluster.add_configmaps(config_map)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=statefulset_namespace,
        name=statefulset_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_statefulset_configmap_existence_positive(
    harness,
    capsys,
):
    check_name = "k8s_statefulset_configmap_existence"

    (
        configmap_name,
        configmap_namespace,
        statefulset_configmap_name,
        statefulset_name,
        statefulset_namespace,
    ) = ("test", "test_ns", "test", "test_statefulset", "test_ns")

    # Create Configmap object
    config_map = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace)
    )

    # Create StatefulSet object
    statefulset = V1StatefulSet(
        metadata=V1ObjectMeta(name=statefulset_name, namespace=statefulset_namespace),
        spec=V1StatefulSetSpec(
            service_name="test_service",
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            config_map=V1ConfigMapVolumeSource(
                                name=statefulset_configmap_name
                            ),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                ),
            ),
            volume_claim_templates=[
                V1PersistentVolumeClaim(
                    metadata=V1ObjectMeta(name="data-volume"),
                    spec=V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources=V1ResourceRequirements(requests={"storage": "1Gi"}),
                        data_source=V1TypedLocalObjectReference(
                            name=statefulset_configmap_name, kind="PersistentVolume"
                        ),
                    ),
                ),
            ],
        ),
    )

    harness.k8s_cluster.add_statefulsets(statefulset)
    harness.k8s_cluster.add_configmaps(config_map)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=statefulset_namespace,
            name=statefulset_name,
            stdout=stdout,
            check_status="PASS",
        )
