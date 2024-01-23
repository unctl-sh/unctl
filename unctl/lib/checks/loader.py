import importlib

from unctl.list import load_checks


class ChecksLoader:
    """
    Gathers all the checks from the checks directory
    """

    def __init__(self, checks_dir="checks"):
        self.checks_dir = checks_dir
        self.check_modules = []

    def _load_check_module(self, module_name):
        module = importlib.import_module(module_name)
        return module

    def load_all(self, provider, categories=None, services=None, checks=None):
        checks = load_checks(
            provider=provider,
            categories=categories,
            services=services,
            checks=checks,
            checks_dir=self.checks_dir,
        )

        for check in checks:
            module = self._load_check_module(check.module)
            self.check_modules.append(module)

        print(f"✅ Loaded {len(self.check_modules)} check(s)")
        return self.check_modules
