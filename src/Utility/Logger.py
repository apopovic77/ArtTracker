import datetime

# Color codes for console output
class ConsoleColors:
    RESET = "\033[0m"
    CYAN = "\033[36m"
    ORANGE = "\033[33m"
    RED = "\033[31m"

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.log_file = None
        self.console_logging = True
        self.file_logging = False

    def set_log_file(self, filename):
        self.log_file = open(filename, "a")
        self.file_logging = True

    def disable_file_logging(self):
        self.log_file = None
        self.file_logging = False

    def enable_file_logging(self):
        self.file_logging = True

    def disable_console_logging(self):
        self.console_logging = False

    def enable_console_logging(self):
        self.console_logging = True

    def log_to_console(self, message, color=ConsoleColors.RESET):
        if self.console_logging:
            print(f"{color}{message}{ConsoleColors.RESET}")

    def log_to_file(self, message):
        if self.file_logging and self.log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_file.write(f"{timestamp}: {message}\n")
            self.log_file.flush()

    def log_error(self, message, exception=None):
        if exception:
            message = f"{message}: {str(exception)}"
        self.log_to_console(f"ERROR: {message}", color=ConsoleColors.RED)
        self.log_to_file(f"ERROR: {message}")

    def log_info(self, message):
        self.log_to_console(f"INFO: {message}", color=ConsoleColors.CYAN)
        self.log_to_file(f"INFO: {message}")

    def log_warning(self, message):
        self.log_to_console(f"WARNING: {message}", color=ConsoleColors.ORANGE)
        self.log_to_file(f"WARNING: {message}")
