import pytest
from kubernetes.client import (
    V1ObjectMeta,
    V1PersistentVolumeClaim,
    V1PersistentVolumeClaimStatus,
)

from test_utils.utils import _common_checks_test


# K8s PVC Pending
@pytest.mark.parametrize(
    [
        "pvc_name",
        "pvc_namespace",
        "phase",
    ],
    [
        # PVC is in 'Pending' phase
        ("test_pvc", "test_ns", "Pending"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_pvc_pending_negative(
    harness,
    capsys,
    pvc_name,
    pvc_namespace,
    phase,
):
    check_name = "k8s_pvc_pending"

    pvc = V1PersistentVolumeClaim(
        metadata=V1ObjectMeta(name=pvc_name, namespace=pvc_namespace),
        status=V1PersistentVolumeClaimStatus(phase=phase),
    )

    harness.k8s_cluster.add_pvcs(pvc)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        name=pvc_name,
        namespace=pvc_namespace,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_pvc_pending_positive(harness, capsys):
    check_name = "k8s_pvc_pending"

    (
        pvc_name,
        pvc_namespace,
        phase,
    ) = ("test_pvc", "test_ns", "Bound")

    pvc = V1PersistentVolumeClaim(
        metadata=V1ObjectMeta(name=pvc_name, namespace=pvc_namespace),
        status=V1PersistentVolumeClaimStatus(phase=phase),
    )

    harness.k8s_cluster.add_pvcs(pvc)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            name=pvc_name,
            namespace=pvc_namespace,
            stdout=stdout,
            check_status="PASS",
        )
