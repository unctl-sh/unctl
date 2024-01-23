import contextlib
import json
from collections import namedtuple
from dataclasses import dataclass
from functools import partial
from unittest.mock import MagicMock, patch

import aiohttp

from test_utils.networking.constants import AdapterNames
from test_utils.utils import InstanceAssignedMagicMock

AIOHTTP_REQUEST_SPEC = namedtuple(
    "AioHTTPRequestSpec", ("method", "url", "args", "kwargs")
)
HTTPX_REQUEST_SPEC = namedtuple("HTTPXRequestSpec", ("method", "url", "request"))


@dataclass
class AIOHTTPResponse:
    status: int
    reason: str
    headers: dict

    response_data: dict

    async def read(self):
        return json.dumps(self.response_data).encode("utf-8")

    def __await__(self):
        async def _inner():
            return self

        return _inner().__await__()


class MockAdapters:
    """
    This adapter serves just 1 purpose: abstract mocking
    networking libraries providing general interface.
    Usage example:
    >>> with MockAdapters.make_adapter(
        "<adapter_name>", "<callable for requests intercepting>"
        ).mock():
    >>>     pass  # at this point all requests from given "<adapter_name>"
    # will be routed to specified callable

    Having multiple pieces of code using multiple http libraries
    it's pretty hard to mock all of them in a standard way.
    This class abstracts 2 crutial parts:
        1. stardardization of mocking process
            1.1. now you have to simply pre-define a mock that should be used
                for mocking a specific library, e.g.:
                >>> MOCK_OBJ = partial(
                        patch.object, urllib3.poolmanager.PoolManager, "urlopen"
                    )
        2. request adaptation
            2.1. each library makes a request in a different format,
                    so it's hard to make a single general mock for all of them
            2.2. in order to solve this, we have a concept of "adaptation",
                 which is basically `build_request` method that's being
                 called for each response, returning standard
                 `HTTP_REQUEST_SPEC` instance
        3. response adaptation
            3.1. each library expects response in a different type/format,
                 in order to achive that, `RESPONSE_TYPE` is used. You specify
                 desired response type, and that type gets propagated through
                 the interceptor to its data source, so that dota source knows
                 which response type to retun back
    """

    ADAPTERS = {}
    MOCK_OBJ = None
    RESPONSE_TYPE = None

    def __init__(self, interceptor_fn):
        self.interceptor_fn = interceptor_fn

    @classmethod
    def __init_subclass__(cls, **kwargs):
        with contextlib.suppress(KeyError):
            cls.ADAPTERS[kwargs["name"]] = cls

    @classmethod
    def make_adapter(cls, name, interceptor_fn):
        adapter_cls = cls.ADAPTERS[name]
        return adapter_cls(interceptor_fn)

    @property
    def original_fn_ref(self):
        """
        Always fetch a new version of a target function/etc
        in order to make possible sequenced mock calls
        """
        raise NotImplementedError

    def build_request(self, *args, **kwargs):
        raise NotImplementedError

    @contextlib.contextmanager
    def mock(self):
        with self.MOCK_OBJ(
            new=InstanceAssignedMagicMock(
                side_effect=self._proxy_mock(self.original_fn_ref)
            )
        ):
            yield

    def _call_parent(self, original_fn_ref, *args, **kwargs):
        return original_fn_ref(*args, **kwargs)

    def _proxy_mock(self, original_fn_ref):
        def inner(*args, **kwargs):
            adapted = self.build_request(*args, **kwargs)
            matched, result = self.interceptor_fn(adapted, self.RESPONSE_TYPE)
            if matched:
                return result
            return self._call_parent(original_fn_ref, *args, **kwargs)

        return inner


class HTTPMockAdapters(MockAdapters):
    def _call_parent(self, original_fn_ref, *args, **kwargs):
        if not isinstance(original_fn_ref, MagicMock):
            # if original `network-adapter` isn't a `MagicMock`,
            # we should not allow that kind of request
            # basically it's prohibited to reach the internet from the tests
            raise RuntimeError(
                f"Tried to access external URL from the tests. "
                f"Request data: {args, kwargs}."
            )
        return original_fn_ref(*args, **kwargs)


class AIOHTTPAdapter(HTTPMockAdapters, name=AdapterNames.AIOHTTP):
    RESPONSE_TYPE = AIOHTTPResponse
    MOCK_OBJ = partial(patch.object, aiohttp.client.ClientSession, "request")

    @property
    def original_fn_ref(self):
        return aiohttp.client.ClientSession.request

    def build_request(self, instance, method, url, *args, **kwargs):
        return AIOHTTP_REQUEST_SPEC(method, url, args, kwargs)
