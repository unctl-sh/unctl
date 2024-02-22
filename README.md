# unctl

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <a href="https://unskript.com/">
        <img src="https://storage.googleapis.com/unskript-website/assets/favicon.png" alt="Logo" width="80" height="80">
    </a>
    <p align="center">
    <a href="https://pypi.org/project/unctl/"><img alt="Python Version" src="https://img.shields.io/pypi/v/unctl.svg"></a>
    <a href="https://pypi.python.org/pypi/unctl/"><img alt="Python Version" src="https://img.shields.io/pypi/pyversions/unctl.svg"></a>
    <a href="https://pypistats.org/packages/unctl"><img alt="PyPI unctl downloads" src="https://img.shields.io/pypi/dw/unctl.svg?label=unctl%20downloads"></a>
</p>
</div>

<!-- TABLE OF CONTENTS -->
<br />
<p align="center">Table of Contents</p>
<ol>
<li>
    <a href="#about-the-project">About The Project</a>
    <ul>
        <li><a href="#health-checks">Health Checks</a></li>
        <li><a href="#list-of-checks">List of Checks</a></li>
        <li><a href="#built-with">Built With</a></li>
    </ul>
</li>
<li>
    <a href="#getting-started">Getting Started</a>
    <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#development">Development</a></li>
        <li><a href="#testing">Testing</a></li>
        <li><a href="#release">Release</a></li>
    </ul>
</li>
<li><a href="#usage">Usage</a></li>
<li><a href="#roadmap">Roadmap</a></li>
<li><a href="#contact">Contact</a></li>
<!-- <li><a href="#acknowledgments">Acknowledgments</a></li> -->
</ol>

<!-- ABOUT THE PROJECT -->
## About The Project

`unctl` is a versatile command-line tool designed to perform a wide range of checks and inspections on various components of your infrastructure. It provides a unified interface to assess the health and performance of different services and platforms, and goes beyond mere diagnosis.

<p align="right">(<a href="#unctl">back to top</a>)</p>

<!-- HEALTH CHECKS -->
### Health Checks
This tools runs the health checks and provides a report.
In order to get access to automated AI based diagnostics and remediations for these problems, go to https://unskript.com/.

<p align="right">(<a href="#unctl">back to top</a>)</p>

### List of Checks
<!-- Do not edit content within these sections, it is auto-generated -->
<!-- GENERATED_CHECKS_GROUPS_SECTION_START -->
| Provider | Checks |
|---|---|
| k8s | 31 |
| mysql | 1 |

<!-- GENERATED_CHECKS_GROUPS_SECTION_END -->
<!-- GENERATED_CHECKS_SECTION_START -->
#### k8s checks
| Check | Service | Category | Severity | Description |
|---|---|---|---|---|
| Check if a k8s PVC is in Pending state. | pvc | Health | Critical | Alerts on pending PVCs, highlighting potential delays in provisioning persistent volume claims for all the namespaces |
| Check if the k8s node is in Ready state. | node | Health | Critical | Ensure node health by examining readiness conditions, signaling failures if any issues are detected in the node's status |
| Deployment has insufficient replicas. | deployment | Health | Critical | Validate Deployments for the correct number of available replicas, highlighting any discrepancies between desired and available counts |
| Pod has a high restart count. | pod | Health | Critical | Identify pods for all the namespaces where certain containers have restarted more than 10 times, indicating potential instability concerns |
| Pod is in CrashLoopBackOff state. | pod | Health | Critical | Identify pods with containers stuck in a CrashLoopBackOff state, highlighting potential issues impacting pod stability for all the namespaces |
| Service has endpoints that are NotReady. | service | Health | Severe | Highlights when services have NotReady endpoints, indicating potential disruptions to service reliability for all the namespaces |
| Service has no endpoints. | service | Health | Severe | Identify services with no associated endpoints, highlighting potential misconfigurations impacting service connectivity |
| Analyzing HPAs, checking if scale targets exist and have resources | pod | HPA | High | Analyze optimal Horizontal Pod Autoscaler (HPA) configurations by ensuring associated resources (Deployments, ReplicationControllers, ReplicaSets, StatefulSets) have defined resource limits for effective auto-scaling |
| Check for the existence of Ingress class, service and secrets for all the namespaces | ingress | Ingress | High | Ensure proper Ingress configurations by validating associated services, secrets, and ingress classes, flagging issues if there are missing elements or misconfigured settings for all the namespaces |
| Check the existence of secret in Daemonset | daemonset | Daemonset, Secret | High | Ensure the presence of referenced Secrets in Daemonset volumes, reporting failures for any missing Secret within all the namespaces |
| Check the existence of secret in Deployment | secret | Deployment | High | Ensure the presence of referenced Secrets in Deployment volumes, reporting failures for any missing Secret for all the namespaces |
| Excessive Pods on Node | node | Resource Limits | High | Assesses nodes for excessive pod counts, flagging potential issues if pods near capacity thresholds based on CPU and memory resources |
| Find Deployments with missing configmap | configmap | Deployment | High | Ensure the presence of referenced ConfigMaps in Deployment volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Find Pending Pods | pod | Health | High | Ensure that Pods are not in a Pending state due to scheduling issues or container creation failures, and report relevant details for diagnostics |
| Find Pods with missing configmap | pod | Pod, ConfigMap | High | Ensure the presence of referenced ConfigMaps in Pod containers and volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Find Pods with missing secrets | pod | Pod, Secret | High | Ensure the presence of referenced Secrets in Pod containers, reporting failures for any missing Secret for all the namespaces |
| Insufficient PIDs on Node | node | Performance | High | Check if the nodes have remaining PIDs less than a set threshold |
| Kubernetes Node Out-of-Memory Check | node | Performance | High | Checks if any Kubernetes node is using more than 85% of its memory capacity. |
| Validate configmap existence in Statefulset | statefulset | StatefulSet | High | Ensure the existence of referenced ConfigMaps in StatefulSet volume claims and template volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Validate cronjob starting deadline | cronjob | CronJob | High | Ensure CronJobs have a non-negative starting deadline, reporting failures for negative values for all the namespaces |
| Validate existence of configmaps in daemonsets | daemonset | DaemonSet, ConfigMap | High | Ensure the presence of referenced ConfigMaps in Daemonset volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Verify StatefulSet has valid service | statefulset | StatefulSet | High | Verify StatefulSet's service reference, ensuring it points to an existing service in all the namespaces, reporting failures for non-existent services |
| Verify StatefulSet has valid storageClass | statefulset | StatefulSet | High | Validate StatefulSet's storage class, ensuring it references existing storage classes in the namespace, reporting failures for non-existent ones |
| Zero Scale Deployment Check | deployment | Availability | High | Verify that Deployments have a non-zero replica count, preventing unintentional scaling down to zero |
| Check if Kubernetes services have matching pod labels | service | Configuration | Medium | This check validates if Kubernetes service selectors match pod labels. This ensures proper routing & discovery of pods. |
| Pod template validation in DaemonSet | daemonset | Resource Management | Medium | Checks that the Pod template within a DaemonSet is configured correctly according to certain threshold values. |
| Services Target Port Match | service | Diagnostic | Medium | This check identifies service ports that do not match their target ports |
| Validate that network policies are in place and configured correctly | networkpolicy | Network Security | Medium | Verify Network Policy configurations, highlighting issues if policies allow traffic to all pods or if not applied to any specific pods |
| Zero scale detected in statefulset | statefulset | Availability | Medium | Check to ensure that no StatefulSets are scaled to zero as it might hamper availability. |
| Find unused DaemonSet | daemonset | DaemonSet, Cost, Resource Optimization | Low | Any DaemonSet that has been created but has no associated pods and remained unused for over 30 days. |
| Validate cronjobs schedule and state | cronjob | CronJob | Low | Ensure CronJobs have valid schedules and are not suspended, reporting failures for any invalid schedules or suspended jobs for all the namespaces |

#### mysql checks
| Check | Service | Category | Severity | Description |
|---|---|---|---|---|
| Checks max used connections | global | Connection, Thread | High | Checks max used connections reaching max count |

<!-- GENERATED_CHECKS_SECTION_END -->

<p align="right">(<a href="#unctl">back to top</a>)</p>

### Built With

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<p align="right">(<a href="#unctl">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
* Python >= 3.10

### Installation

1. Get distibution on your machine:
    * Run `pip` command to install `unctl` from [PyPI](https://pypi.org/project/unctl/)
        ```sh
        pip install unctl
        ```

#### Kubernetes

1. (optional) Set `KUBECONFIG` variable to specific location other than default:
   ```sh
   export KUBECONFIG=<path to kube config file>
   ```
2. Run unctl command to see list of options:
   ```sh
   unctl k8s -h
   ```

#### MySQL

1. unctl is using `~/.my.cnf` as [config path](https://dev.mysql.com/doc/refman/8.0/en/option-files.html).
2. Run unctl command to see list of options:
   ```sh
   unctl mysql -h
   ```

<p align="right">(<a href="#unctl">back to top</a>)</p>


### Development
1. Install [poetry](https://python-poetry.org/):
    ```sh
    pip install poetry
    ```
2. Enter virtual env:
    ```sh
    poetry shell
    ```
3. Install dependencies:
    ```sh
    poetry install
    ```
4. Run tool:
    ```sh
    python unctl.py -h
    ```
5. Format all files before commit changes:
    ```sh
    black .
    ```

<p align="right">(<a href="#unctl">back to top</a>)</p>
   
### Testing

See the testing documentation <a href="docs/testing-framework.md">here</a>.

<p align="right">(<a href="#unctl">back to top</a>)</p>

### Release

For the release this repo is using [Semantic Realese](https://semver.org/) as automated process. To be able to generate changelogs we should keep using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) practice. When PR merged to `master` it uses `squash and merge` with PR title for the commit message. This requires `PR title` to be conventional:
```
feat(EN-4444): Add Button component
^    ^          ^
|    |          |__ Subject
|    |_______ Scope
|____________ Type
```

When release job is running it will automatically bump up version depends on the changes:

1. `BREAKING CHANGE: <message>` - creates new major version
2. `feat: <message>` - creates new minor version
3. `fix or perf: <message>` - creates new patch version
4. [All other tags](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#commit-parser-options-dict-str-any) will not create new release


<p align="right">(<a href="#unctl">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### unctl
```sh
% unctl -h
usage: unctl [-h] [-v] {k8s,mysql} ...

          Welcome to unSkript CLI Interface 

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit

unctl available providers:
  {k8s,mysql}

To see the different available options on a specific provider, run:
        unctl {provider} -h|--help
```

### Provider
```sh
% unctl {provider} -h
usage: unctl {provider} [-h] [-f] [-c CHECKS [CHECKS ...]] [--sort-by {object,check}] [--categories CATEGORIES [CATEGORIES ...]]
                 [--services SERVICES [SERVICES ...]] [-l] [--list-categories] [--list-services] [-e | --explain | --no-explain]
                 [-r | --remediate | --no-remediate]

options:
  -h, --help            show this help message and exit
  -f, --failing-only    Show only failing checks
  -c CHECKS [CHECKS ...], --checks CHECKS [CHECKS ...]
                        Filter checks by IDs
  --sort-by {object,check}
                        Sort results by 'object' (default) or 'check'
  --categories CATEGORIES [CATEGORIES ...]
                        Filter checks by category
  --services SERVICES [SERVICES ...]
                        Filter checks by services
  -l, --list-checks     List available checks
  --list-categories     List available categories
  --list-services       List available services

Licensed features:
  These features available only in a licensed version.

  -e, --explain, --no-explain
                        Explain failures
  -r, --remediate, --no-remediate
                        Create remediation plan
```


<p align="right">(<a href="#unctl">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [ ] K8s checks - in progress
- [ ] MySQL checks - in progress
- [ ] ElasticSearch checks
- [ ] AWS checks
- [ ] GCP checks

<p align="right">(<a href="#unctl">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Abhishek Saxena: abhishek@unskript.com

Official website: https://unskript.com/

<p align="right">(<a href="#unctl">back to top</a>)</p>
