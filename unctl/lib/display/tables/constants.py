from enum import Enum

UNSET = object()


class TableNames(str, Enum):
    SORTED_BY_OBJECT = "sorted_by_object"
    SORTED_BY_CHECKS = "sorted_by_checks"
    LIST_CHECKS = "list_checks"
