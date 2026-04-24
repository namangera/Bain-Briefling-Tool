import logging
import os
import sys

LOG_FILE = "/tmp/app.log"
_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    if not _configured:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

        root = logging.getLogger()
        root.setLevel(level)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(fmt)

        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(fmt)

        root.addHandler(stdout_handler)
        root.addHandler(file_handler)

        _configured = True

    return logging.getLogger(name)
