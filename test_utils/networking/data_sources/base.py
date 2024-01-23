from collections import namedtuple
from dataclasses import dataclass, field

INTERCEPTOR_SPEC = namedtuple("InterceptorSpec", ("callable", "spec"))


@dataclass
class BaseDataSource:
    _interceptors: list = field(init=False)

    def __post_init__(self):
        self._interceptors = self.collect_interceptors()

    def collect_interceptors(self):
        specs = []
        for name, attribute in vars(type(self)).items():
            if not getattr(attribute, "__intercepting__", False):
                continue
            spec = INTERCEPTOR_SPEC(callable=getattr(self, name), spec=attribute.spec)
            specs.append(spec)
        return specs

    def __interceptor_missing__(self, request, response_type):
        return NotImplemented

    def __call__(self, request, response_type):
        # make it replaceable by any callable object (duck-typing)
        # if no response can be found, should raise `LookupError`
        return self.route(request, response_type)

    def route(self, request, response_type):
        response = None
        for spec in self._interceptors:
            is_valid, context = spec.spec.validate(request)
            if is_valid:
                response = spec.callable(request, response_type, context)
                break
        return self._finish(request, response, response_type)

    def _finish(self, request, response, response_type):
        if not response:
            response = self.__interceptor_missing__(request, response_type)
            if response is NotImplemented:
                raise LookupError(request)
        if not isinstance(response, response_type):
            raise TypeError(f"Expected: {response_type}, got: {type(response)}")
        return response
