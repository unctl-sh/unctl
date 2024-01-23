import pytest
from kubernetes.client import (
    V1ObjectMeta,
    V1Pod,
    V1ContainerStatus,
    V1ContainerState,
    V1ContainerStateWaiting,
    V1Container,
    V1PodSpec,
    V1PodStatus,
)

from test_utils.utils import _common_checks_test


# K8s Pod CrashLoopBackOff
@pytest.mark.parametrize(
    [
        "pod_name",
        "pod_namespace",
        "container_name",
        "waiting_reason",
    ],
    [
        # container status is in waiting state and the reason is 'CrashLoopBackOff'
        ("test_pod", "test_ns", "test_container", "CrashLoopBackOff"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_pod_crashloopbackoff_negative(
    harness,
    capsys,
    pod_name,
    pod_namespace,
    container_name,
    waiting_reason,
):
    check_name = "k8s_pod_crashloopbackoff"

    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    image="test",
                )
            ]
        ),
        status=V1PodStatus(
            container_statuses=[
                V1ContainerStatus(
                    image="test",
                    image_id="test1",
                    ready=False,
                    restart_count=5,
                    name=container_name,
                    state=V1ContainerState(
                        waiting=V1ContainerStateWaiting(
                            reason=waiting_reason,
                        )
                    ),
                )
            ]
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
async def test_k8s_pod_crashloopbackoff_positive(harness, capsys):
    check_name = "k8s_pod_crashloopbackoff"

    (
        pod_name,
        pod_namespace,
        container_name,
        waiting_reason,
    ) = ("test_pod", "test_ns", "test_container", "ContainerCreating")

    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    image="test",
                )
            ]
        ),
        status=V1PodStatus(
            container_statuses=[
                V1ContainerStatus(
                    image="test",
                    image_id="test1",
                    ready=False,
                    restart_count=5,
                    name=container_name,
                    state=V1ContainerState(
                        waiting=V1ContainerStateWaiting(
                            reason=waiting_reason,
                        )
                    ),
                )
            ]
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
