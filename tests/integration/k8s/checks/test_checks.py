import pytest
from kubernetes.client import (
    V1ConfigMap,
    V1ObjectMeta,
    V1Deployment,
    V1DeploymentSpec,
    V1PodTemplateSpec,
    V1PodSpec,
    V1Volume,
    V1ConfigMapVolumeSource,
    V1LabelSelector,
    V1CronJob,
    V1CronJobSpec,
    V1JobTemplateSpec,
    V1JobSpec,
    V1NetworkPolicy,
    V1NetworkPolicySpec,
    V1Pod,
    V1Secret,
    V1DaemonSet,
    V1DaemonSetSpec,
    V1SecretVolumeSource,
    V1Container,
    V1EnvVar,
    V1EnvVarSource,
    V1ConfigMapKeySelector,
    V1SecretKeySelector,
    V1DeploymentStatus,
)


def _common_checks_test(check_result, *, namespace, name, check_status, stdout):
    assert check_result.status == check_status, "unexpected check status"
    assert (
        check_result.resource_namespace == namespace
    ), "invalid namespace set on the check report"
    assert (
        check_result.resource_name == name
    ), "invalid resource set on the check report"

    # verify that all required info got printed to the user
    assert "Loaded 1 check(s)" in stdout
    assert (
        check_result.check_metadata.CheckTitle in stdout
    ), "no check title found in stdout"


# Deployment configmap existence
@pytest.mark.parametrize(
    [
        "configmap_name",
        "volume_configmap_name",
        "config_namespace",
        "deployment_name",
        "deployment_namespace",
    ],
    [
        # namespace matches, but configmap name do not
        (
            "test_configmap",
            "another_configmap",
            "test_ns",
            "test_deployment",
            "test_ns",
        ),
        # config name matches, but namespace name do not
        ("test_configmap", "test_configmap", "test_ns", "test_deployment", "test"),
    ],
)
@pytest.mark.asyncio
async def test_k8s_deployment_configmap_existence_negative(
    harness,
    capsys,
    configmap_name,
    volume_configmap_name,
    config_namespace,
    deployment_name,
    deployment_namespace,
):
    check_name = "k8s_deployment_configmap_existence"

    config_map = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=config_namespace)
    )
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            config_map=V1ConfigMapVolumeSource(
                                name=volume_configmap_name
                            ),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_configmaps(config_map)
    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=deployment_namespace,
        name=deployment_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_deployment_configmap_existence_positive(harness, capsys):
    check_name = "k8s_deployment_configmap_existence"
    deployment_name = "test_deployment"

    configmap_name, volume_configmap_name, config_namespace, deployment_namespace = (
        "test_configmap",
        "test_configmap",
        "test_ns",
        "test_ns",
    )

    config_map = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=config_namespace)
    )
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            config_map=V1ConfigMapVolumeSource(
                                name=volume_configmap_name
                            ),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_configmaps(config_map)
    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)
    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=deployment_namespace,
            name=deployment_name,
            stdout=stdout,
            check_status="PASS",
        )


# Cronjob with negative starting deadline
@pytest.mark.parametrize(
    [
        "cronjob_name",
        "cronjob_namespace",
        "starting_deadline_seconds",
    ],
    [
        # starting_deadline_seconds has a negative value
        ("test_cronjob", "test_ns", -90),
    ],
)
@pytest.mark.asyncio
async def test_k8s_cronjob_with_negative_starting_deadline_negative(
    harness,
    capsys,
    cronjob_name,
    cronjob_namespace,
    starting_deadline_seconds,
):
    check_name = "k8s_cronjob_with_negative_starting_deadline"

    cronjob = V1CronJob(
        metadata=V1ObjectMeta(name=cronjob_name, namespace=cronjob_namespace),
        spec=V1CronJobSpec(
            schedule="0 0 * * *",
            starting_deadline_seconds=starting_deadline_seconds,
            job_template=V1JobTemplateSpec(
                spec=V1JobSpec(
                    template=V1PodTemplateSpec(spec=V1PodSpec(containers=[]))
                )
            ),
        ),
    )

    harness.k8s_cluster.add_cronjobs(cronjob)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=cronjob_namespace,
        name=cronjob_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_cronjob_with_negative_starting_deadline_positive(harness, capsys):
    check_name = "k8s_cronjob_with_negative_starting_deadline"

    cronjob_name, cronjob_namespace, starting_deadline_seconds = (
        "test_cronjob",
        "test_ns",
        90,
    )

    cronjob = V1CronJob(
        metadata=V1ObjectMeta(name=cronjob_name, namespace=cronjob_namespace),
        spec=V1CronJobSpec(
            schedule="0 0 * * *",
            starting_deadline_seconds=starting_deadline_seconds,
            job_template=V1JobTemplateSpec(
                spec=V1JobSpec(
                    template=V1PodTemplateSpec(spec=V1PodSpec(containers=[]))
                )
            ),
        ),
    )

    harness.k8s_cluster.add_cronjobs(cronjob)

    results = await harness.k8s_cluster.run_check(check_name)
    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=cronjob_namespace,
            name=cronjob_name,
            stdout=stdout,
            check_status="PASS",
        )


@pytest.mark.parametrize(
    [
        "netpol_name",
        "pod_name",
        "netpol_namespace",
        "pod_namespace",
        "match_labels",
        "pod_labels",
    ],
    [
        # match_label is not present in the network_policy
        (
            "test_network_policy",
            "test_pod",
            "test_ns",
            "test_ns",
            None,
            {"app": "value"},
        ),
        # match_label is present but its not present in the pod.metadata.labels
        (
            "test_network_policy",
            "test_pod",
            "test_ns",
            "test_ns",
            {"app": "value1"},
            {"app": "value2"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_netpol_negative(
    harness,
    capsys,
    netpol_name,
    pod_name,
    netpol_namespace,
    pod_namespace,
    match_labels,
    pod_labels,
):
    check_name = "k8s_netpol"
    # Creating a Network Policy object
    netpol = V1NetworkPolicy(
        metadata=V1ObjectMeta(name=netpol_name, namespace=netpol_namespace),
        spec=V1NetworkPolicySpec(
            pod_selector=V1LabelSelector(match_labels=match_labels),
        ),
    )

    # Creating a Pod object
    pod = V1Pod(
        metadata=V1ObjectMeta(
            name=pod_name, namespace=pod_namespace, labels=pod_labels
        ),
    )

    harness.k8s_cluster.add_network_policies(netpol)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]

    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=netpol_namespace,
        name=netpol_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_netpol_positive(harness, capsys):
    check_name = "k8s_netpol"
    netpol_name, pod_name, netpol_namespace, pod_namespace, match_labels, pod_labels = (
        "test_network_policy",
        "test_pod",
        "test_ns",
        "test_ns",
        {"app": "value"},
        {"app": "value"},
    )

    netpol = V1NetworkPolicy(
        metadata=V1ObjectMeta(name=netpol_name, namespace=netpol_namespace),
        spec=V1NetworkPolicySpec(
            pod_selector=V1LabelSelector(match_labels=match_labels),
        ),
    )

    pod = V1Pod(
        metadata=V1ObjectMeta(
            name=pod_name, namespace=pod_namespace, labels=pod_labels
        ),
    )

    harness.k8s_cluster.add_network_policies(netpol)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=netpol_namespace,
            name=netpol_name,
            stdout=stdout,
            check_status="PASS",
        )


@pytest.mark.parametrize(
    [
        "daemonset_name",
        "daemonset_namespace",
        "volume_secret_name",
        "secret_name",
        "secret_namespace",
    ],
    [
        # namespace matches, but secret name do not
        (
            "test_daemonset",
            "test_ns",
            "test_secret2",
            "test_secret1",
            "test_ns",
        ),
        # secret name matches, but namespace name do not
        (
            "test_daemonset",
            "test_ns2",
            "test_secret",
            "test_secret",
            "test_ns1",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_daemonset_secret_existence_negative(
    harness,
    capsys,
    daemonset_name,
    daemonset_namespace,
    volume_secret_name,
    secret_name,
    secret_namespace,
):
    check_name = "k8s_daemonset_secret_existence"
    # Creating a secret object
    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    # Creating a daemonset object
    daemonset = V1DaemonSet(
        metadata=V1ObjectMeta(name=daemonset_name, namespace=daemonset_namespace),
        spec=V1DaemonSetSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            secret=V1SecretVolumeSource(secret_name=volume_secret_name),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_daemonsets(daemonset)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=daemonset_namespace,
        name=daemonset_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_daemonset_secret_existence_positive(harness, capsys):
    check_name = "k8s_daemonset_secret_existence"
    (
        daemonset_name,
        daemonset_namespace,
        volume_secret_name,
        secret_name,
        secret_namespace,
    ) = (
        "test_daemonset",
        "test_ns",
        "test_secret",
        "test_secret",
        "test_ns",
    )

    # Creating a secret object
    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    # Creating a daemonset object
    daemonset = V1DaemonSet(
        metadata=V1ObjectMeta(name=daemonset_name, namespace=daemonset_namespace),
        spec=V1DaemonSetSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            secret=V1SecretVolumeSource(secret_name=volume_secret_name),
                            name="test_volume",
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_daemonsets(daemonset)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=daemonset_namespace,
            name=daemonset_name,
            stdout=stdout,
            check_status="PASS",
        )


# Pod configmap existence
@pytest.mark.parametrize(
    [
        "pod_name",
        "pod_namespace",
        "container_name",
        "env_var_name",
        "pod_configmap_key",
        "volume_configmap_name",
        "container_configmap_name",
        "configmap_name",
        "configmap_namespace",
    ],
    [
        # namespace matches, but configmap name do not
        (
            "test_pod",
            "test_ns",
            "test_container",
            "test_env_var",
            "test_configmap_key",
            "test_configmap2",
            "test_configmap2",
            "test_configmap1",
            "test_ns",
        ),
        # configmap name matches, but namespace name do not
        (
            "test_pod",
            "test_ns1",
            "test_container",
            "test_env_var",
            "test_configmap_key",
            "test_configmap",
            "test_configmap",
            "test_configmap",
            "test_ns2",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_pod_configmap_existence_negative(
    harness,
    capsys,
    pod_name,
    pod_namespace,
    container_name,
    env_var_name,
    pod_configmap_key,
    volume_configmap_name,
    container_configmap_name,
    configmap_name,
    configmap_namespace,
):
    check_name = "k8s_pod_configmap_existence"

    # Creating a config_map object
    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace)
    )
    # Creating a pod object
    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    env=[
                        V1EnvVar(
                            name=env_var_name,
                            value_from=V1EnvVarSource(
                                config_map_key_ref=V1ConfigMapKeySelector(
                                    key=pod_configmap_key,
                                    name=container_configmap_name,
                                )
                            ),
                        )
                    ],
                )
            ],
            volumes=[
                V1Volume(
                    name="config-map-volume",
                    config_map=V1ConfigMapVolumeSource(
                        name=volume_configmap_name,
                    ),
                )
            ],
        ),
    )

    harness.k8s_cluster.add_configmaps(configmap)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=pod_namespace,
        name=pod_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_pod_configmap_existence_positive(harness, capsys):
    check_name = "k8s_pod_configmap_existence"
    (
        pod_name,
        pod_namespace,
        container_name,
        env_var_name,
        pod_configmap_key,
        volume_configmap_name,
        container_configmap_name,
        configmap_name,
        configmap_namespace,
    ) = (
        "test_pod",
        "test_ns",
        "test_container",
        "test_env_var",
        "test_configmap_key",
        "test_configmap",
        "test_configmap",
        "test_configmap",
        "test_ns",
    )

    # Creating a config_map object
    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace)
    )
    # Creating a pod object
    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    env=[
                        V1EnvVar(
                            name=env_var_name,
                            value_from=V1EnvVarSource(
                                config_map_key_ref=V1ConfigMapKeySelector(
                                    key=pod_configmap_key,
                                    name=container_configmap_name,
                                )
                            ),
                        )
                    ],
                )
            ],
            volumes=[
                V1Volume(
                    name="config-map-volume",
                    config_map=V1ConfigMapVolumeSource(
                        name=volume_configmap_name,
                    ),
                )
            ],
        ),
    )

    harness.k8s_cluster.add_configmaps(configmap)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=pod_namespace,
            name=pod_name,
            stdout=stdout,
            check_status="PASS",
        )


# Pod secret existence
@pytest.mark.parametrize(
    [
        "pod_name",
        "pod_namespace",
        "container_name",
        "env_var_name",
        "pod_secret_name",
        "pod_secret_key",
        "secret_name",
        "secret_namespace",
    ],
    [
        # namespace matches, but secret name do not
        (
            "test_pod",
            "test_ns",
            "test_container",
            "test_env_var",
            "test_secret1",
            "test_secret_key",
            "test_secret2",
            "test_ns",
        ),
        # secret name matches, but namespace name do not
        (
            "test_pod",
            "test_ns1",
            "test_container",
            "test_env_var",
            "test_secret",
            "test_secret_key",
            "test_secret",
            "test_ns2",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_pod_secret_existence_negative(
    harness,
    capsys,
    pod_name,
    pod_namespace,
    container_name,
    env_var_name,
    pod_secret_name,
    pod_secret_key,
    secret_name,
    secret_namespace,
):
    check_name = "k8s_pod_secret_existence"
    # Creating a secret object
    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    # Creating a pod object
    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    env=[
                        V1EnvVar(
                            name=env_var_name,
                            value_from=V1EnvVarSource(
                                secret_key_ref=V1SecretKeySelector(
                                    key=pod_secret_key,
                                    name=pod_secret_name,
                                    optional=None,
                                )
                            ),
                        )
                    ],
                )
            ],
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=pod_namespace,
        name=pod_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_pod_secret_existence_positive(harness, capsys):
    check_name = "k8s_pod_secret_existence"
    (
        pod_name,
        pod_namespace,
        container_name,
        env_var_name,
        pod_secret_name,
        pod_secret_key,
        secret_name,
        secret_namespace,
    ) = (
        "test_pod",
        "test_ns",
        "test_container",
        "test_env_var",
        "test_secret",
        "test_secret_key",
        "test_secret",
        "test_ns",
    )

    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    # Creating a pod object
    pod = V1Pod(
        metadata=V1ObjectMeta(name=pod_name, namespace=pod_namespace),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    env=[
                        V1EnvVar(
                            name=env_var_name,
                            value_from=V1SecretKeySelector(
                                name=pod_secret_name,
                                key=pod_secret_key,
                            ),
                        )
                    ],
                )
            ],
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_pods(pod)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=pod_namespace,
            name=pod_name,
            stdout=stdout,
            check_status="PASS",
        )


# Daemonset configmap existence
@pytest.mark.parametrize(
    [
        "daemonset_name",
        "daemonset_namespace",
        "volume_configmap_name",
        "configmap_name",
        "configmap_namespace",
    ],
    [
        # namespace matches, but configmap name do not
        (
            "test_daemonset",
            "test_ns",
            "test_configmap2",
            "test_configmap1",
            "test_ns",
        ),
        # configmap name matches, but namespace name do not
        (
            "test_daemonset",
            "test_ns2",
            "test_configmap",
            "test_configmap",
            "test_ns1",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_daemonset_configmap_existence_negative(
    harness,
    capsys,
    daemonset_name,
    daemonset_namespace,
    volume_configmap_name,
    configmap_name,
    configmap_namespace,
):
    check_name = "k8s_daemonset_configmap_existence"

    # Creating a configmap object
    config_map = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace)
    )

    # Creating a daemonset object
    daemonset = V1DaemonSet(
        metadata=V1ObjectMeta(name=daemonset_name, namespace=daemonset_namespace),
        spec=V1DaemonSetSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            name="test_volume",
                            config_map=V1ConfigMapVolumeSource(
                                name=volume_configmap_name
                            ),
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_configmaps(config_map)
    harness.k8s_cluster.add_daemonsets(daemonset)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=daemonset_namespace,
        name=daemonset_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_daemonset_configmap_existence_positive(harness, capsys):
    check_name = "k8s_daemonset_configmap_existence"
    (
        daemonset_name,
        daemonset_namespace,
        volume_configmap_name,
        configmap_name,
        configmap_namespace,
    ) = (
        "test_daemonset",
        "test_ns",
        "test_configmap",
        "test_configmap",
        "test_ns",
    )

    # Creating a configmap object
    config_map = V1ConfigMap(
        metadata=V1ObjectMeta(name=configmap_name, namespace=configmap_namespace)
    )

    # Creating a daemonset object
    daemonset = V1DaemonSet(
        metadata=V1ObjectMeta(name=daemonset_name, namespace=daemonset_namespace),
        spec=V1DaemonSetSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    volumes=[
                        V1Volume(
                            name="test_volume",
                            config_map=V1ConfigMapVolumeSource(
                                name=volume_configmap_name
                            ),
                        )
                    ],
                    containers=[],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_configmaps(config_map)
    harness.k8s_cluster.add_daemonsets(daemonset)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=daemonset_namespace,
            name=daemonset_name,
            stdout=stdout,
            check_status="PASS",
        )


# Deployment insufficient replicas
@pytest.mark.parametrize(
    ["deployment_name", "deployment_namespace", "replicas", "available_replicas"],
    [
        # the number of replicas and available replicas are mismatched
        (
            "test_deployment",
            "test_ns",
            1,
            2,
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_deployment_insufficient_replicas_negative(
    harness, capsys, deployment_name, deployment_namespace, replicas, available_replicas
):
    check_name = "k8s_deployment_insufficient_replicas"
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            replicas=replicas,
            template=V1PodTemplateSpec(),
            selector=V1LabelSelector(),
        ),
        status=V1DeploymentStatus(available_replicas=available_replicas),
    )

    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=deployment_namespace,
        name=deployment_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_k8s_deployment_insufficient_replicas_positive(harness, capsys):
    check_name = "k8s_deployment_insufficient_replicas"
    deployment_name = "test_deployment"

    deployment_namespace, replicas, available_replicas = (
        "test_ns",
        1,
        1,
    )

    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            replicas=replicas,
            template=V1PodTemplateSpec(),
            selector=V1LabelSelector(),
        ),
        status=V1DeploymentStatus(available_replicas=available_replicas),
    )

    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)

    stdout, _ = capsys.readouterr()
    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=deployment_namespace,
            name=deployment_name,
            stdout=stdout,
            check_status="PASS",
        )


# Deployment secret existence
@pytest.mark.parametrize(
    [
        "deployment_name",
        "deployment_namespace",
        "secret_name",
        "secret_namespace",
        "deployment_secret_key",
        "deployment_secret_key_name",
    ],
    [
        # namespace matches, but secret name do not
        (
            "test_deployment",
            "test_ns",
            "test_secret1",
            "test_ns",
            "test_secret_key",
            "test_secret2",
        ),
        # secret name matches, but namespace name do not
        (
            "test_deployment",
            "test_ns1",
            "test_secret",
            "test_ns2",
            "test_secret_key",
            "test_secret",
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_deployment_secret_existence_negative(
    harness,
    capsys,
    deployment_name,
    deployment_namespace,
    secret_name,
    secret_namespace,
    deployment_secret_key,
    deployment_secret_key_name,
):
    check_name = "k8s_deployment_secret_existence"

    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            env=[
                                V1EnvVar(
                                    name="test_env_var",
                                    value_from=V1EnvVarSource(
                                        secret_key_ref=V1SecretKeySelector(
                                            key=deployment_secret_key,
                                            name=deployment_secret_key_name,
                                        )
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()
    _common_checks_test(
        check_result,
        namespace=deployment_namespace,
        name=deployment_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_deployment_secret_existence_positive(harness, capsys):
    check_name = "k8s_deployment_secret_existence"
    deployment_name = "test_deployment"
    (
        deployment_namespace,
        secret_name,
        secret_namespace,
        deployment_secret_key,
        deployment_secret_key_name,
    ) = (
        "test_ns",
        "test_secret",
        "test_ns",
        "test_secret_key",
        "test_secret",
    )

    secret = V1Secret(
        metadata=V1ObjectMeta(name=secret_name, namespace=secret_namespace)
    )
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=deployment_name, namespace=deployment_namespace),
        spec=V1DeploymentSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test_container",
                            env=[
                                V1EnvVar(
                                    name="test_env_var",
                                    value_from=V1EnvVarSource(
                                        secret_key_ref=V1SecretKeySelector(
                                            key=deployment_secret_key,
                                            name=deployment_secret_key_name,
                                        )
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ),
            selector=V1LabelSelector(),
        ),
    )

    harness.k8s_cluster.add_secrets(secret)
    harness.k8s_cluster.add_deployments(deployment)

    results = await harness.k8s_cluster.run_check(check_name)
    stdout, _ = capsys.readouterr()
    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=deployment_namespace,
            name=deployment_name,
            stdout=stdout,
            check_status="PASS",
        )


# Cronjob with suspended or invalid schedule
@pytest.mark.parametrize(
    [
        "cronjob_name",
        "cronjob_namespace",
        "schedule",
        "suspend",
    ],
    [
        # cronjob is suspended
        (
            "test_cronjob",
            "test_ns",
            "0 0 1 1 *",
            True,
        ),
        # cronjob has incorrect schedule
        (
            "test_cronjob",
            "test_ns",
            "* * * * * * *",
            False,
        ),
    ],
)
@pytest.mark.asyncio
async def test_k8s_cronjobs_suspended_or_invalid_schedule_negative(
    harness,
    capsys,
    cronjob_name,
    cronjob_namespace,
    schedule,
    suspend,
):
    check_name = "k8s_cronjobs_suspended_or_invalid_schedule"
    cronjob = V1CronJob(
        metadata=V1ObjectMeta(name=cronjob_name, namespace=cronjob_namespace),
        spec=V1CronJobSpec(
            schedule=schedule,
            suspend=suspend,
            job_template=V1JobTemplateSpec(
                spec=V1JobSpec(
                    template=V1PodTemplateSpec(spec=V1PodSpec(containers=[]))
                )
            ),
        ),
    )

    harness.k8s_cluster.add_cronjobs(cronjob)

    results = await harness.k8s_cluster.run_check(check_name)
    check_result = results[check_name][0]
    stdout, _ = capsys.readouterr()

    _common_checks_test(
        check_result,
        namespace=cronjob_namespace,
        name=cronjob_name,
        stdout=stdout,
        check_status="FAIL",
    )


@pytest.mark.asyncio
async def test_k8s_cronjobs_suspended_or_invalid_schedule_positive(harness, capsys):
    check_name = "k8s_cronjobs_suspended_or_invalid_schedule"
    cronjob_name, cronjob_namespace, schedule, suspend = (
        "test_cronjob",
        "test_ns",
        "0 0 1 1 *",
        False,
    )

    cronjob = V1CronJob(
        metadata=V1ObjectMeta(name=cronjob_name, namespace=cronjob_namespace),
        spec=V1CronJobSpec(
            schedule=schedule,
            suspend=suspend,
            job_template=V1JobTemplateSpec(
                spec=V1JobSpec(
                    template=V1PodTemplateSpec(spec=V1PodSpec(containers=[]))
                )
            ),
        ),
    )

    harness.k8s_cluster.add_cronjobs(cronjob)

    results = await harness.k8s_cluster.run_check(check_name)
    stdout, _ = capsys.readouterr()

    for check_result in results[check_name]:
        _common_checks_test(
            check_result,
            namespace=cronjob_namespace,
            name=cronjob_name,
            stdout=stdout,
            check_status="PASS",
        )
