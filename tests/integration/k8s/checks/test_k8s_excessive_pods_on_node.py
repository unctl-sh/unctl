import pytest
from kubernetes.client import V1Node, V1ObjectMeta, V1Pod, V1PodSpec, V1NodeStatus

from test_utils.utils import _common_checks_test


# Excessive pods on nodes
@pytest.mark.parametrize(
    [
        "node_name",
        "pod_names",
        "pod_namespace",
        "cpu_allocatable",
        "memory_allocatable",
    ],
    [
        # if value of 'cpu_allocatable' is such that 'pod_count' is greater than
        # 'max_cpu_pods * 0.8' calculated from the k8s check
        (
            "test_node",
            ["test_pod1", "test_pod2", "test_pod3", "test_pod4", "test_pod5"],
            "test_ns",
            "190m",
            "6180536Ki",
        ),
        # if value of 'memory_allocatable' is such that 'pod_count' is greater than
        # 'max_mem_pods * 0.8' calculated from the k8s check
        (
            "test_node",
            ["test_pod1", "test_pod2", "test_pod3", "test_pod4", "test_pod5"],
            "test_ns",
            "1930m",
            "618053Ki",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_excessive_pods_on_node_negative(
    harness,
    capsys,
    node_name,
    pod_names,
    pod_namespace,
    cpu_allocatable,
    memory_allocatable,
):
    check_name = "k8s_excessive_pods_on_node"

    # Create a list of V1Pod objects
    pods = [
        V1Pod(
            metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
            spec=V1PodSpec(node_name=node_name, containers=[]),
        )
        for pod_name in pod_names
    ]

    node = V1Node(
        metadata=V1ObjectMeta(name=node_name),
        status=V1NodeStatus(
            allocatable={
                "cpu": cpu_allocatable,
                "memory": memory_allocatable,
            },
        ),
    )

    harness.k8s_cluster.add_nodes(node)
    # Use unpacking operator to pass each pod as a separate argument
    harness.k8s_cluster.add_pods(*pods)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        name=node_name,
        namespace="",
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_excessive_pods_on_node_positive(harness, capsys):
    check_name = "k8s_excessive_pods_on_node"

    (
        node_name,
        pod_names,
        pod_namespace,
        cpu_allocatable,
        memory_allocatable,
    ) = (
        "test_node",
        ["test_pod1", "test_pod2", "test_pod3", "test_pod4", "test_pod5"],
        "test_ns",
        "1930m",
        "6180536Ki",
    )

    # Create a list of V1Pod objects
    pods = [
        V1Pod(
            metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
            spec=V1PodSpec(node_name=node_name, containers=[]),
        )
        for pod_name in pod_names
    ]

    node = V1Node(
        metadata=V1ObjectMeta(name=node_name),
        status=V1NodeStatus(
            allocatable={
                "cpu": cpu_allocatable,
                "memory": memory_allocatable,
            }
        ),
    )

    harness.k8s_cluster.add_nodes(node)
    # Use unpacking operator to pass each pod as a separate argument
    harness.k8s_cluster.add_pods(*pods)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace="",
            name=node_name,
            stdout=stdout,
            check_status="PASS",
        )
