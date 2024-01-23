import pytest
from kubernetes.client import (
    V1StatefulSet,
    V1ObjectMeta,
    V1Service,
    V1StatefulSetSpec,
    V1LabelSelector,
    V1PodTemplateSpec,
    V1PodSpec,
)

from test_utils.utils import _common_checks_test


# Statefulset service validation
@pytest.mark.parametrize(
    [
        "service_name",
        "service_namespace",
        "statefulset_service_name",
        "statefulset_name",
        "statefulset_namespace",
    ],
    [
        # service name matches but namespace does not match
        ("test", "test_ns1", "test", "test_statefulset", "test_ns2"),
        # namespace matches but service name does not match
        ("test1", "test_ns", "test2", "test_statefulset", "test_ns"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_statefulset_service_validation_negative(
    harness,
    capsys,
    service_name,
    service_namespace,
    statefulset_service_name,
    statefulset_name,
    statefulset_namespace,
):
    check_name = "k8s_statefulset_service_validation"

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
    )

    # Create StatefulSet object
    statefulset = V1StatefulSet(
        kind="StatefulSet",
        metadata=V1ObjectMeta(name=statefulset_name, namespace=statefulset_namespace),
        spec=V1StatefulSetSpec(
            service_name=statefulset_service_name,
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    containers=[],
                ),
            ),
        ),
    )

    harness.k8s_cluster.add_statefulsets(statefulset)
    harness.k8s_cluster.add_services(service)

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
async def test_k8s_statefulset_service_validation_positive(
    harness,
    capsys,
):
    check_name = "k8s_statefulset_service_validation"

    (
        service_name,
        service_namespace,
        statefulset_service_name,
        statefulset_name,
        statefulset_namespace,
    ) = ("test", "test_ns", "test", "test_statefulset", "test_ns")

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
    )

    # Create StatefulSet object
    statefulset = V1StatefulSet(
        kind="StatefulSet",
        metadata=V1ObjectMeta(name=statefulset_name, namespace=statefulset_namespace),
        spec=V1StatefulSetSpec(
            service_name=statefulset_service_name,
            selector=V1LabelSelector(match_labels={"app": "label"}),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": "label"}),
                spec=V1PodSpec(
                    containers=[],
                ),
            ),
        ),
    )

    harness.k8s_cluster.add_statefulsets(statefulset)
    harness.k8s_cluster.add_services(service)

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
