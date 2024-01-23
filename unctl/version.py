import json
import requests
import toml
from importlib.metadata import version

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

from colorama import Fore, Style


def current():
    try:
        return toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except Exception:
        return version(__package__)


def check():
    if last() > parse(current()):
        print(
            f"{Fore.YELLOW}A new release of unctl is available: "
            f"{Fore.RED + Style.BRIGHT}{current()}{Style.RESET_ALL} -> "
            f"{Fore.GREEN + Style.BRIGHT}{last()}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.YELLOW}To update, run: "
            f"{Fore.GREEN + Style.BRIGHT}pip install --upgrade unctl{Style.RESET_ALL}"
        )


def last():
    """Return version of package on pypi.python.org using json."""
    url = f"https://pypi.python.org/pypi/{__package__}/json"
    req = requests.get(url, timeout=3)
    version = parse("0")
    if req.status_code == requests.codes.ok:
        j = json.loads(req.text.encode(req.encoding))
        releases = j.get("releases", [])
        for release in releases:
            ver = parse(release)
            if not ver.is_prerelease:
                version = max(version, ver)
    return version
