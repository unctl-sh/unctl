import pytest
from kubernetes.client import (
    V1Service,
    V1ObjectMeta,
    V1Endpoints,
    V1EndpointSubset,
    V1EndpointAddress,
)

from test_utils.utils import _common_checks_test


# K8s Service Empty
@pytest.mark.parametrize(
    [
        "service_name",
        "service_namespace",
        "endpoint_name",
    ],
    [
        # service name and endpoint name are not the same
        ("test1", "test_ns", "test2"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_service_empty_negative(
    harness,
    capsys,
    service_name,
    service_namespace,
    endpoint_name,
):
    check_name = "k8s_service_empty"

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
        spec={"selector": {"app": "label"}},
    )

    # Create Endpoint object
    endpoint = V1Endpoints(
        metadata=V1ObjectMeta(name=endpoint_name),
        subsets=[
            V1EndpointSubset(
                addresses=[
                    V1EndpointAddress(ip="10.0.0.1"),
                    V1EndpointAddress(ip="10.0.0.2"),
                ],
                ports=[{"port": 8080}],
            )
        ],
    )

    harness.k8s_cluster.add_services(service)
    harness.k8s_cluster.add_endpoints(endpoint)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=service_namespace,
        name=service_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_service_empty_positive(
    harness,
    capsys,
):
    check_name = "k8s_service_empty"

    (
        service_name,
        service_namespace,
        endpoint_name,
    ) = ("test", "test_ns", "test")

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
        spec={"selector": {"app": "label"}},
    )

    # Create Endpoint object
    endpoint = V1Endpoints(
        metadata=V1ObjectMeta(name=endpoint_name),
        subsets=[
            V1EndpointSubset(
                addresses=[
                    V1EndpointAddress(ip="10.0.0.1"),
                    V1EndpointAddress(ip="10.0.0.2"),
                ],
                ports=[{"port": 8080}],
            )
        ],
    )

    harness.k8s_cluster.add_services(service)
    harness.k8s_cluster.add_endpoints(endpoint)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=service_namespace,
            name=service_name,
            stdout=stdout,
            check_status="PASS",
        )
