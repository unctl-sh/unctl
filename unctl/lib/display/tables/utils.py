from colorama import Fore, Style


def get_severity(check):
    severity_color = (
        Fore.RED
        if check.check_metadata.Severity == "Critical"
        else (Fore.YELLOW if check.check_metadata.Severity == "Severe" else Fore.WHITE)
    )
    return severity_color + check.check_metadata.Severity + Style.RESET_ALL
