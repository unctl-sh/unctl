from collections import namedtuple

from prettytable import PrettyTable

from unctl.lib.display.tables.constants import UNSET

HEADER_PROCESSOR_SPEC = namedtuple("HeaderProcessorSpec", ("header_name", "processor"))


class BaseTable:
    HEADERS = None
    TABLE_REGISTRY = {}

    def __init__(
        self, results, display, context=None, initial_table=None, divider=False
    ):
        self.results = results
        self.display = display
        self.context = context or {}
        self.initial_table = initial_table or PrettyTable()
        self.divider = divider
        self._processors = self._collect_header_processors()

    def __init_subclass__(cls, **kwargs):
        for provider in kwargs["providers"]:
            cls.TABLE_REGISTRY[(provider, kwargs["name"])] = cls

    @classmethod
    def get_table_builder_for(cls, provider, table_name):
        return cls.TABLE_REGISTRY[(provider, table_name)]

    @classmethod
    def configure(
        cls, results, display, context=None, initial_table=None, divider=False
    ):
        return cls(results, display, context, initial_table, divider)

    def _build_table_for(self):
        rows, headers = [], []

        collect_headers = True
        for result in self.results:
            row = []
            for processor in self._processors:
                row_value = processor.processor(result, self.context)
                if row_value is UNSET:
                    continue
                if collect_headers:
                    header = processor.header_name
                    if header in headers:
                        raise RuntimeError("Duplicate header: " + header)
                    headers.append(header)
                row.append(row_value)
            collect_headers = False
            rows.append(row)
        self.initial_table.field_names = headers
        for row in rows:
            self.initial_table.add_row(row, divider=self.divider)
        return self.initial_table

    def _collect_header_processors(self):
        processors = []
        for name, attr in vars(type(self)).items():
            if not getattr(attr, "__header_processor__", False):
                continue
            processors.append(
                HEADER_PROCESSOR_SPEC(attr._header_name, getattr(self, name))  # noqa
            )
        processors.sort(key=lambda proc: self.HEADERS.index(proc.header_name))  # noqa
        return processors

    def build(self):
        return self._build_table_for()


# triggering tables to register
from unctl.lib.display.tables.mysql import *  # noqa
from unctl.lib.display.tables.common import *  # noqa
from unctl.lib.display.tables.k8s import *  # noqa
