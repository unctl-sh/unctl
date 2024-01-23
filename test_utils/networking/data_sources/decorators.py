from test_utils.networking.data_sources.specs import (
    HTTPInterceptorSpec,
)


def http_intercepts(http_method, url, api_version="v1"):
    def wrapper(f):
        f.__intercepting__ = True
        f.spec = HTTPInterceptorSpec(
            http_method, ("/".join((api_version, url)) if api_version else url)
        )
        return f

    return wrapper
