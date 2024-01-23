import pytest
from kubernetes.client import (
    V1ObjectMeta,
    V1Pod,
    V1Container,
    V1PodSpec,
    V1PodStatus,
)

from test_utils.utils import _common_checks_test


# K8s Pods Pending
@pytest.mark.parametrize(
    [
        "pod_name",
        "pod_namespace",
        "pod_phase",
    ],
    [
        # when pod.status.phase is "Pending"
        (
            "test_pod",
            "test_ns",
            "Pending",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_pods_pending_negative(
    harness,
    capsys,
    pod_name,
    pod_namespace,
    pod_phase,
):
    check_name = "k8s_pods_pending"

    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test_container",
                    image="test",
                )
            ]
        ),
        status=V1PodStatus(
            phase=pod_phase,
            conditions=[
                {
                    "type": "test_type",
                    "status": "Unknown",
                    "reason": "Unschedulable",
                }
            ],
        ),
    )

    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        name=pod_name,
        namespace=pod_namespace,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_pods_pending_positive(harness, capsys):
    check_name = "k8s_pods_pending"

    (
        pod_name,
        pod_namespace,
        pod_phase,
    ) = ("test_pod", "test_ns", "Running")

    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test_container",
                    image="test",
                )
            ]
        ),
        status=V1PodStatus(
            phase=pod_phase,
            conditions=[
                {
                    "type": "Ready",
                    "status": "True",
                    "reason": "Unschedulable",
                }
            ],
        ),
    )

    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            name=pod_name,
            namespace=pod_namespace,
            stdout=stdout,
            check_status="PASS",
        )
