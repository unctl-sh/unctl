import pytest
from kubernetes.client import (
    V1Node,
    V1ObjectMeta,
)

from test_utils.utils import _common_checks_test


# Node Ready
@pytest.mark.parametrize(
    ["node_name", "node_type", "node_status"],
    [
        # node type is 'Ready' and node status is not equal to 'True'
        ("test_node", "Ready", "False"),
        # node status is not equal to 'False' irrespective of node type
        ("test_node", "OutOfDisk", "True"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_node_ready_negative(
    harness,
    capsys,
    node_name,
    node_type,
    node_status,
):
    check_name = "k8s_node_ready"

    # Create Node object
    node = V1Node(
        metadata=V1ObjectMeta(
            name=node_name,
            labels={"key": "value"},
        ),
        status={
            "conditions": [
                {
                    "type": node_type,
                    "status": node_status,
                }
            ],
        },
    )

    harness.k8s_cluster.add_nodes(node)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace="",
        name=node_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_node_ready_positive(
    harness,
    capsys,
):
    check_name = "k8s_node_ready"

    (
        node_name,
        node_type,
        node_status,
    ) = ("test_node", "Ready", "True")

    # Create Node object
    node = V1Node(
        metadata=V1ObjectMeta(
            name=node_name,
            labels={"key": "value"},
        ),
        status={
            "conditions": [
                {
                    "type": node_type,
                    "status": node_status,
                }
            ],
        },
    )

    harness.k8s_cluster.add_nodes(node)

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
