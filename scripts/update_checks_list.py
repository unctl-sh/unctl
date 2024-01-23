from itertools import groupby

from unctl.list import load_checks


def update_readme_section(file_path, section, checks_list):
    readme_path = file_path
    start_comment = f"<!-- {section}_START -->"
    end_comment = f"<!-- {section}_END -->"

    try:
        with open(readme_path, "r") as file:
            readme_content = file.read()

        start_index = readme_content.find(start_comment)
        end_index = readme_content.find(end_comment)

        if start_index != -1 and end_index != -1:
            updated_content = f"{start_comment}\n{checks_list}\n{end_comment}"
            updated_readme = (
                f"{readme_content[:start_index]}{updated_content}"
                f"{readme_content[end_index + len(end_comment):]}"
            )

            with open(readme_path, "w") as file:
                file.write(updated_readme)

        else:
            raise Exception(f"Could not find start and end comments in {readme_path}.")

    except FileNotFoundError:
        raise Exception(f"{readme_path} not found. Please make sure the file exists.")


def update_checks_groups(grouped_objects: dict):
    new_checks_groups = "| Provider | Checks |\n|---|---|\n"
    for group in grouped_objects:
        new_checks_groups += f"| {group} | {len(grouped_objects[group])} |\n"

    update_readme_section(
        "README.md", "GENERATED_CHECKS_GROUPS_SECTION", new_checks_groups
    )


def update_checks(grouped_objects: dict):
    providers = []
    for group in grouped_objects:
        group_checks = f"#### {group} checks\n"
        group_checks += (
            "| Check | Service | Category | Severity | Description |\n"
            "|---|---|---|---|---|\n"
        )

        checks = grouped_objects[group]

        for check in checks:
            check_md = check.check_metadata
            group_checks += (
                f"| {check_md.CheckTitle} | {check_md.ServiceName} | "
                f"{', '.join(check_md.Categories)} | {check_md.Severity} | "
                f"{check_md.Description} |\n"
            )

        providers.append(group_checks)

    new_checks = "\n".join(providers)

    update_readme_section("README.md", "GENERATED_CHECKS_SECTION", new_checks)


if __name__ == "__main__":
    checks = load_checks()

    severity_mapping = {
        "Critical": 1,
        "Severe": 2,
        "High": 3,
        "Medium": 4,
        "Low": 5,
    }

    sorted_checks = sorted(
        checks,
        key=lambda check: (
            check.check_metadata.Provider,
            severity_mapping[check.check_metadata.Severity],
            check.check_metadata.CheckTitle,
        ),
    )

    grouped_objects = {
        key: list(group)
        for key, group in groupby(
            sorted_checks, key=lambda check: check.check_metadata.Provider
        )
    }

    update_checks_groups(grouped_objects)
    update_checks(grouped_objects)

    print("README updated successfully.")
