import builtins
import contextlib
import contextvars
import copy
import os
from types import MethodType
from unittest.mock import MagicMock, mock_open, patch

INTERCEPTING_ACTIVE = contextvars.ContextVar("InterceptingActive", default=False)


@contextlib.contextmanager
def set_context(var, value):
    token = var.set(value)
    try:
        yield
    finally:
        var.reset(token)


class InstanceAssignedMagicMock(MagicMock):
    """
    By default, `MagicMock` doesn't propagate the instance
    if used to mock a class method.
    So we need to explicitly make a relation
    with the callable mock and the target instance.
    """

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return MethodType(self, instance)

    def _increment_mock_call(self, /, *args, **kwargs):
        # remove first argument (the instance reference to patched object)
        # to preserve existing interface of `assert_called_with`/etc
        args = args[1:]
        return super()._increment_mock_call(*args, **kwargs)


@contextlib.contextmanager
def fake_file(path, data):
    original_open = builtins.open

    def _mock_open(filename, *args, **kwargs):
        if path != filename:
            return original_open(filename, *args, **kwargs)
        return mock_open(read_data=data)()

    with patch("builtins.open", side_effect=_mock_open) as mock_file:
        yield mock_file


@contextlib.contextmanager
def fake_env(**env):
    environ = copy.deepcopy(os.environ)
    environ.update(env)

    with patch.dict(os.environ, environ) as fake_environ:
        yield fake_environ


def get_test_config(provider, filename):
    config_dir = os.path.abspath(os.path.join(__file__, f"../configs/{provider}"))
    for path in os.scandir(config_dir):
        if path.is_file() and path.name == filename:
            with open(path.path) as fp:
                return fp.read()


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
