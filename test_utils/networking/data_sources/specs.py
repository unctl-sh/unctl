import abc
import re


class BaseInterceptorSpec(abc.ABC):
    @abc.abstractmethod
    def validate(self, request):
        raise NotImplementedError


class HTTPInterceptorSpec(BaseInterceptorSpec):
    def __init__(self, http_method, url):
        self.http_method = http_method

        escaped_url = re.escape(url)
        pattern = re.sub(r"\\{[^/]+}", r"[^/]+", escaped_url)
        self.url_pattern = f"^.*/{pattern}[^/]*$"

    def validate(self, request):
        matched = re.match(self.url_pattern, request.url) is not None
        valid = self.http_method == request.method and matched
        return valid, None
