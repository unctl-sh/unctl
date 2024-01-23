import contextlib
from collections import UserList

from test_utils.networking.adapters import MockAdapters
from test_utils.networking.constants import AdapterNames
from test_utils.networking.data_sources.base import BaseDataSource
from test_utils.utils import (
    INTERCEPTING_ACTIVE,
    set_context,
)


class InterceptorHistory(UserList):
    @property
    def top(self):
        with contextlib.suppress(IndexError):
            return self.data[-1]

    @property
    def length(self):
        return len(self)

    def filter(self, fn):
        return [item for item in self if fn(item)]


class BaseInterceptor:
    """
    Hooks inbetween urllib3 and Kubernetes library.

    Intercepting all requests to whatever adapter you choose and routing them
    to appropriate data source methods.

    Simple dependency graph:
    Data Source <-> URL Interceptor <-> Network Adapter <-> Any HTTP library
    <-> Request -> Response

    You should not be using this class directly, use `Harness` instead.
    """

    ADAPTERS = None

    def __init__(self, data_source):
        """
        Takes `data_source` in order to route intercepted request.
        A `data_source` should basically be a testing cluster object.
        """
        self.data_source = data_source
        self.history = InterceptorHistory()

    @classmethod
    def create_interceptor_for(cls, source):
        if not isinstance(source, BaseDataSource):
            raise TypeError
        return cls(source)

    def __call__(self, request, response_type):
        with set_context(INTERCEPTING_ACTIVE, True):
            try:
                response = self.data_source(request, response_type)
                self.history.append(request)
                return True, response
            except LookupError:
                return False, None

    @contextlib.contextmanager
    def intercept(self):
        with contextlib.ExitStack() as stack:
            for adapter in self.ADAPTERS:
                stack.enter_context(MockAdapters.make_adapter(adapter, self).mock())
            yield


class BaseApiUrlInterceptor(BaseInterceptor):
    BASE_URL = None

    def __call__(self, request, *args, **kwargs):
        if not request.url.startswith(self.BASE_URL):
            return False, None
        return super().__call__(request, *args, **kwargs)


class UrllibInterceptor(BaseApiUrlInterceptor):
    ADAPTERS = [AdapterNames.AIOHTTP]


class K8SApiUrlInterceptor(UrllibInterceptor):
    BASE_URL = "http://test-cluster/"
