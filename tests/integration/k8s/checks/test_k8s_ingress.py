import pytest
from kubernetes.client import (
    V1Ingress,
    V1ObjectMeta,
    V1IngressSpec,
    V1IngressRule,
    V1HTTPIngressRuleValue,
    V1HTTPIngressPath,
    V1IngressBackend,
    V1IngressTLS,
    V1IngressServiceBackend,
    V1ServiceBackendPort,
    V1IngressClass,
    V1Service,
    V1Secret,
)

from test_utils.utils import _common_checks_test


# Ingress
@pytest.mark.parametrize(
    [
        "ingress_name",
        "ingress_namespace",
        "ingress_class_name",
        "ingress_class_value",
        "ingressclass_name",
        "ingress_service_name",
        "service_name",
        "service_namespace",
        "ingress_tls_secret_name",
        "secret_name",
        "secret_namespace",
    ],
    [
        # ingress_class_name is None and ingress_class_value is None
        # (i.e. class name from ingress does not match with those with ingressclasses)
        (
            "test_ingress",
            "test_ns",
            None,
            None,
            "test_class_name",
            "test_service",
            "test_service",
            "test_ns",
            "test_secret",
            "test_secret",
            "test_ns",
        ),
        # ingress_class_name does not match with class name from ingressclasses
        (
            "test_ingress",
            "test_ns",
            "test_class_name1",
            "test_class_value",
            "test_class_name2",
            "test_service",
            "test_service",
            "test_ns",
            "test_secret",
            "test_secret",
            "test_ns",
        ),
        # service name, namespace from ingress does match with service name and
        # namespace from the services
        # service_name matches but namespace does not match
        (
            "test_ingress",
            "test_ns1",
            "test_class_name",
            "test_class_value",
            "test_class_name",
            "test_service",
            "test_service",
            "test_ns2",
            "test_secret",
            "test_secret",
            "test_ns1",
        ),
        # namespace matches but service_name does not match
        (
            "test_ingress",
            "test_ns",
            "test_class_name",
            "test_class_value",
            "test_class_name",
            "test_service1",
            "test_service2",
            "test_ns",
            "test_secret",
            "test_secret",
            "test_ns",
        ),
        # tls_secret_name, namespace from ingress does match with secret name and
        # secret namespace from the list of secrets
        # tls_secret_name matches but namespace does not match
        (
            "test_ingress",
            "test_ns1",
            "test_class_name",
            "test_class_value",
            "test_class_name",
            "test_service",
            "test_service",
            "test_ns1",
            "test_secret",
            "test_secret",
            "test_ns2",
        ),
        # namespace matches but tls_secret_name does not match
        (
            "test_ingress",
            "test_ns",
            "test_class_name",
            "test_class_value",
            "test_class_name",
            "test_service",
            "test_service",
            "test_ns",
            "test_secret1",
            "test_secret2",
            "test_ns",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_ingress_negative(
    harness,
    capsys,
    ingress_name,
    ingress_namespace,
    ingress_class_name,
    ingress_class_value,
    ingressclass_name,
    ingress_service_name,
    service_name,
    service_namespace,
    ingress_tls_secret_name,
    secret_name,
    secret_namespace,
):
    check_name = "k8s_ingress"

    # Create Ingress object
    ingress = V1Ingress(
        metadata=V1ObjectMeta(
            name=ingress_name,
            namespace=ingress_namespace,
            annotations={
                "kubernetes.io/ingress.class": ingress_class_value,
            },
        ),
        spec=V1IngressSpec(
            ingress_class_name=ingress_class_name,
            rules=[
                V1IngressRule(
                    host="example.com",
                    http=V1HTTPIngressRuleValue(
                        paths=[
                            V1HTTPIngressPath(
                                backend=V1IngressBackend(
                                    service=V1IngressServiceBackend(
                                        name=ingress_service_name,
                                        port=V1ServiceBackendPort(
                                            number=80,
                                        ),
                                    ),
                                ),
                                path="/path1",
                                path_type="Prefix",
                            ),
                        ],
                    ),
                ),
            ],
            tls=[
                V1IngressTLS(
                    hosts=["example.com"], secret_name=ingress_tls_secret_name
                ),
            ],
        ),
    )

    # Create Ingressclass object
    ingressclass = V1IngressClass(
        metadata=V1ObjectMeta(name=ingressclass_name),
    )

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
    )

    # Create Secret object
    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace),
    )

    harness.k8s_cluster.add_ingresses(ingress)
    harness.k8s_cluster.add_ingressclasses(ingressclass)
    harness.k8s_cluster.add_services(service)
    harness.k8s_cluster.add_secrets(secret)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=ingress_namespace,
        name=ingress_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_ingress_positive(harness, capsys):
    check_name = "k8s_ingress"

    (
        ingress_name,
        ingress_namespace,
        ingress_class_name,
        ingress_class_value,
        ingressclass_name,
        ingress_service_name,
        service_name,
        service_namespace,
        ingress_tls_secret_name,
        secret_name,
        secret_namespace,
    ) = (
        "test_ingress",
        "test_ns",
        "test_class_name",
        "test_class_value",
        "test_class_name",
        "test_service",
        "test_service",
        "test_ns",
        "test_secret",
        "test_secret",
        "test_ns",
    )

    # Create Ingress object
    ingress = V1Ingress(
        metadata=V1ObjectMeta(
            name=ingress_name,
            namespace=ingress_namespace,
            annotations={
                "kubernetes.io/ingress.class": ingress_class_value,
            },
        ),
        spec=V1IngressSpec(
            ingress_class_name=ingress_class_name,
            rules=[
                V1IngressRule(
                    host="example.com",
                    http=V1HTTPIngressRuleValue(
                        paths=[
                            V1HTTPIngressPath(
                                backend=V1IngressBackend(
                                    service=V1IngressServiceBackend(
                                        name=ingress_service_name,
                                        port=V1ServiceBackendPort(
                                            number=80,
                                        ),
                                    ),
                                ),
                                path="/path1",
                                path_type="Prefix",
                            ),
                        ],
                    ),
                ),
            ],
            tls=[
                V1IngressTLS(
                    hosts=["example.com"], secret_name=ingress_tls_secret_name
                ),
            ],
        ),
    )

    # Create Ingressclass object
    ingressclass = V1IngressClass(
        metadata=V1ObjectMeta(name=ingressclass_name),
    )

    # Create Service object
    service = V1Service(
        metadata=V1ObjectMeta(name=service_name, namespace=service_namespace),
    )

    # Create Secret object
    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace),
    )

    harness.k8s_cluster.add_ingresses(ingress)
    harness.k8s_cluster.add_ingressclasses(ingressclass)
    harness.k8s_cluster.add_services(service)
    harness.k8s_cluster.add_secrets(secret)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=ingress_namespace,
            name=ingress_name,
            stdout=stdout,
            check_status="PASS",
        )
