from PyQt5 import QtCore

# TODO: Use logging system instead of print
DEBUG = True

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
NOTICE = "NOTICE"

LOG_COLOR = {
    INFO: "<font color=\"Black\">",
    WARNING: "<font color=\"Magenta\">",
    ERROR: "<font color=\"Red\">",
    NOTICE: "<font color=\"Blue\">",
    }

END_HTML = "</font><br>"

class Logging(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    # Fix AttributeError: 'Logging' object has no attribute 'flush'
    def flush(self):
        pass


def print_log(level, message):
    formatted_msg = ("%s%s%s%s%s" %(LOG_COLOR[level], level, ": ", message, END_HTML))
    print(formatted_msg)
    print("\n")


def log_info(message):
    if DEBUG:
        print_log(INFO, message)


def log_notice(message):
    print_log(NOTICE, message)


def log_warning(message):
    print_log(WARNING, message)


def log_error(message):
    print_log(ERROR, message)


switcher = {
    INFO: log_info,
    WARNING: log_warning,
    ERROR: log_error
}


def log(level, message):
    func = switcher.get(level, "nothing")
    return func(message)
