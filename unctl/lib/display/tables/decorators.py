def header_processor(header_name):
    def wrapper(func):
        func.__header_processor__ = True
        func._header_name = header_name
        return func

    return wrapper
