from enum import Enum


class CheckProviders(str, Enum):
    K8S = "k8s"
    MySQL = "mysql"
