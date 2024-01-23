import os
import json
from typing import List, Dict
from unctl.lib.checks.check_report import CheckReport


def load_checks(
    provider=None, categories=None, services=None, checks=None, checks_dir="checks"
) -> List[CheckReport]:
    checks_list = []

    check_root = os.path.join(os.path.dirname(__file__), checks_dir)

    for provider_dir in os.listdir(check_root):
        if provider and provider != provider_dir:
            continue

        for check_name in os.listdir(os.path.join(check_root, provider_dir)):
            check_md_path = os.path.join(
                check_root, provider_dir, check_name, f"{check_name}.json"
            )

            if not os.path.isfile(check_md_path):
                continue

            module_name = (
                f"{__package__}.{checks_dir}.{provider_dir}.{check_name}.{check_name}"
            )

            with open(check_md_path, "r") as metadata_file:
                metadata = json.load(metadata_file)

                # Check if the check matches the criteria
                provider_match = not provider or provider == metadata["Provider"]
                categories_match = not categories or any(
                    cat in metadata["Categories"] for cat in categories
                )
                services_match = not services or metadata["ServiceName"] in services
                checks_match = not checks or metadata["CheckID"] in checks

                if all(
                    [provider_match, categories_match, services_match, checks_match]
                ):
                    # Your code here

                    # Extract the required information
                    check = CheckReport(json.dumps(metadata))
                    check.module = module_name

                    checks_list.append(check)

    return checks_list


def get_services(provider=None) -> Dict[str, int]:
    checks = load_checks(provider)
    unique_services = {}
    for check in checks:
        service_name = check.check_metadata.ServiceName
        unique_services[service_name] = unique_services.get(service_name, 0) + 1
    return unique_services


def get_categories(provider=None) -> Dict[str, int]:
    checks = load_checks(provider)
    unique_categories = {}
    for check in checks:
        for category in check.check_metadata.Categories:
            unique_categories[category] = unique_categories.get(category, 0) + 1
    return unique_categories
