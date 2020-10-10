import logging
import sys
from pathlib import Path

Path("logs").mkdir(parents=True, exist_ok=True)


def get_logger(name):
    # init
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # file logger
    fh = logging.FileHandler("logs/" + name + '.log', encoding="UTF-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # console logger
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    return log
