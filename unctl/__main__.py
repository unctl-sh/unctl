import asyncio
import sys
import textwrap
from argparse import ArgumentParser, RawTextHelpFormatter, BooleanOptionalAction

from unctl.constants import CheckProviders
from unctl.lib.checks.loader import ChecksLoader
from unctl.lib.display.display import Displays
from unctl.list import load_checks, get_categories, get_services
from unctl.scanrkube import JobDefinition, ResourceChecker, DataCollector
from unctl.version import check, current


class PrivateFeatureAction(BooleanOptionalAction):
    ERROR_MESSAGE = (
        "argument {options}:"
        "\n\nThis feature is not available in free version. "
        "Please request demo by the link https://unskript.com/"
    )

    def __call__(self, parser, *args, **kwargs):
        super().__call__(parser, *args, **kwargs)
        parser.error(self.ERROR_MESSAGE.format(options="/".join(self.option_strings)))


def add_demo_cli_flags(parser):
    group = parser.add_argument_group(
        "Private features",
        description="These features available only in a private version.",
    )
    group.add_argument(
        "-e",
        "--explain",
        help="Explain failures",
        action=PrivateFeatureAction,
    )
    group.add_argument(
        "-r",
        "--remediate",
        help="Create remediation plan",
        action=PrivateFeatureAction,
    )


def unctl_process_args(argv=None):
    parser = ArgumentParser(
        prog="unctl",
        description="\n\t  Welcome to unSkript CLI Interface \n",
        formatter_class=RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """
            To see the different available options on a specific provider, run:
            \tunctl {provider} -h|--help
            """
        ),
    )
    common_parent_parser = ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(
        title="unctl available providers", dest="provider", required=True
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=current(),
    )
    common_parent_parser.add_argument(
        "-f",
        "--failing-only",
        help="Show only failing checks",
        action="store_true",
    )
    common_parent_parser.add_argument(
        "-c",
        "--checks",
        help="Filter checks by IDs",
        nargs="+",
    )
    common_parent_parser.add_argument(
        "--sort-by",
        choices=["object", "check"],
        default="object",
        help="Sort results by 'object' (default) or 'check'",
    )
    common_parent_parser.add_argument(
        "--categories",
        help="Filter checks by category",
        nargs="+",
        default=None,
    )
    common_parent_parser.add_argument(
        "--services",
        help="Filter checks by services",
        nargs="+",
        default=None,
    )
    common_parent_parser.add_argument(
        "-l",
        "--list-checks",
        help="List available checks",
        action="store_true",
    )
    common_parent_parser.add_argument(
        "--list-categories",
        help="List available categories",
        action="store_true",
    )
    common_parent_parser.add_argument(
        "--list-services",
        help="List available services",
        action="store_true",
    )
    add_demo_cli_flags(common_parent_parser)

    subparsers.add_parser(name=CheckProviders.K8S.value, parents=[common_parent_parser])
    subparsers.add_parser(
        name=CheckProviders.MySQL.value, parents=[common_parent_parser]
    )
    args = parser.parse_args(args=argv)

    return args


def _get_app(options, display=None):
    display = display or Displays.get_display(options.provider)
    loader = ChecksLoader()
    check_modules = loader.load_all(
        provider=options.provider,
        categories=options.categories,
        services=options.services,
        checks=options.checks,
    )
    # Create a job definition
    job_definer = JobDefinition(check_modules)
    jobs = job_definer.generate_jobs()
    print("✅ Created jobs")

    # collect inventory
    collector = DataCollector.make_collector(options.provider)
    print("✅ Collected Kubernetes data")

    app = ResourceChecker(display, collector, jobs, options.provider)
    return app


def process(options):
    display = Displays.get_display(options.provider)
    display.init(options)

    if options.list_checks:
        checks_metadata = load_checks(
            provider=options.provider,
            categories=options.categories,
            services=options.services,
            checks=options.checks,
        )
        display.display_list_checks_table(checks_metadata)
        sys.exit()

    if options.list_categories:
        categories = get_categories(provider=options.provider)
        display.display_grouped_data("Category", categories)
        sys.exit()

    if options.list_services:
        services = get_services(provider=options.provider)
        display.display_grouped_data("Service", services)
        sys.exit()

    app = _get_app(options, display=display)
    results = asyncio.run(app.execute())

    # explanations not needed: print and exit
    display.display_results_table(results, sort_by=options.sort_by)
    return results, app.failing_reports, None


def unctl(argv=None):
    # check version and notify if new version released
    check()
    options = unctl_process_args(argv)
    process(options)


if __name__ == "__main__":
    sys.exit(unctl())
