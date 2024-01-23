import pytest
from kubernetes.client import (
    V1StatefulSet,
    V1ObjectMeta,
    V1PodSpec,
    V1PersistentVolumeClaim,
    V1StatefulSetSpec,
    V1PodTemplateSpec,
    V1ResourceRequirements,
    V1LabelSelector,
    V1PersistentVolumeClaimSpec,
    V1StorageClass,
)

from test_utils.utils import _common_checks_test


# Statefulset storageClass validation
@pytest.mark.parametrize(
    [
        "statefulset_name",
        "statefulset_namespace",
        "statefulset_storageclass_name",
        "storageclass_name",
    ],
    [
        # storageclass name does not match
        ("test", "test_ns", "test_storageclass1", "test_storageclass2"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_statefulset_storage_class_validation_negative(
    harness,
    capsys,
    statefulset_name,
    statefulset_namespace,
    statefulset_storageclass_name,
    storageclass_name,
):
    check_name = "k8s_statefulset_storage_class_validation"

    # Create storageclass object
    storageclass = V1StorageClass(
        metadata=V1ObjectMeta(name=storageclass_name), provisioner="test_provisioner"
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
                    containers=[],
                ),
            ),
            volume_claim_templates=[
                V1PersistentVolumeClaim(
                    metadata=V1ObjectMeta(name="data-volume"),
                    spec=V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources=V1ResourceRequirements(requests={"storage": "1Gi"}),
                        storage_class_name=statefulset_storageclass_name,
                    ),
                )
            ],
        ),
    )

    harness.k8s_cluster.add_storage_classes(storageclass)
    harness.k8s_cluster.add_statefulsets(statefulset)

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
async def test_k8s_statefulset_storage_class_validation_positive(
    harness,
    capsys,
):
    check_name = "k8s_statefulset_storage_class_validation"

    (
        statefulset_name,
        statefulset_namespace,
        statefulset_storageclass_name,
        storageclass_name,
    ) = ("test", "test_ns", "test_storageclass", "test_storageclass")

    # Create storageclass object
    storageclass = V1StorageClass(
        metadata=V1ObjectMeta(name=storageclass_name), provisioner="test_provisioner"
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
                    containers=[],
                ),
            ),
            volume_claim_templates=[
                V1PersistentVolumeClaim(
                    metadata=V1ObjectMeta(name="data-volume"),
                    spec=V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources=V1ResourceRequirements(requests={"storage": "1Gi"}),
                        storage_class_name=statefulset_storageclass_name,
                    ),
                )
            ],
        ),
    )

    harness.k8s_cluster.add_storage_classes(storageclass)
    harness.k8s_cluster.add_statefulsets(statefulset)

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
