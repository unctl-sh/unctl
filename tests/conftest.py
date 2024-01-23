import functools
import os
from contextlib import ExitStack
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import kubernetes.client.models
import pytest

from test_utils.harness import Harness
from test_utils.utils import (
    InstanceAssignedMagicMock,
    INTERCEPTING_ACTIVE,
    get_test_config,
)


@pytest.fixture(autouse=True, scope="session")
def make_k8s_models_reverse_serializable():
    def _replace(target, new_f):
        original_f = getattr(target, new_f.__name__)

        @functools.wraps(original_f)
        def inner(*args, **kwargs):
            ret = original_f(*args, **kwargs)
            return new_f(*args, ret, **kwargs)

        return inner

    def to_dict(self, result):
        if not INTERCEPTING_ACTIVE.get():
            return result
        for k in list(result):
            result[self.attribute_map[k]] = result.pop(k)
        return result

    stack = ExitStack()
    with stack:
        for model in vars(kubernetes.client.models).values():
            if hasattr(model, "to_dict"):
                stack.enter_context(
                    patch.object(
                        model,
                        "to_dict",
                        new=InstanceAssignedMagicMock(
                            side_effect=_replace(model, to_dict)
                        ),
                    )
                )
        yield


@pytest.fixture
def _k8s_temp_config():
    k8s_config = get_test_config(provider="k8s", filename="config.yaml")

    with NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix="yaml", delete=False
    ) as fp:
        fp.write(k8s_config)
    return fp


@pytest.fixture(autouse=True)
def configure_k8s(_k8s_temp_config):
    try:
        with patch(
            "kubernetes_asyncio.config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION",
            _k8s_temp_config.name,
        ):
            yield
    finally:
        _k8s_temp_config.close()
        if not _k8s_temp_config.delete:
            os.unlink(_k8s_temp_config.name)


@pytest.fixture
def harness():
    h = Harness.create()
    with h.spin_up():
        yield h
