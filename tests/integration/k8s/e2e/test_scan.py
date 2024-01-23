import json
import os
import pytest

from unittest.mock import patch

from unctl.__main__ import unctl_process_args


def load_snapshot_data(filename):
    data_path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(data_path, "r") as file:
        return json.load(file)


@pytest.fixture
def snapshot_data():
    data = {
        "pods": load_snapshot_data("snapshot_pods.json"),
        "deployments": load_snapshot_data("snapshot_deployments.json"),
        "services": load_snapshot_data("snapshot_services.json"),
    }

    return data


@pytest.mark.parametrize(
    ["args", "total_checks", "failed_items"],
    [
        (["k8s"], 31, 57),  # full scan
        (["k8s", "-c", "k8s_pods_pending"], 1, 1),  # single check scan
    ],
)
def test_scan(
    harness,
    snapshot_data,
    args,
    total_checks,
    failed_items,
):
    harness.k8s_cluster.add_pods(*snapshot_data["pods"])
    harness.k8s_cluster.add_deployments(*snapshot_data["deployments"])
    harness.k8s_cluster.add_services(*snapshot_data["services"])

    # provide args
    options = unctl_process_args(args)

    # run unctl
    with patch("builtins.input", return_value="n"):
        results, failing_objects, _ = harness.run_unctl(options=options)

    assert len(results) == total_checks

    assert len(failing_objects) == failed_items

    return
