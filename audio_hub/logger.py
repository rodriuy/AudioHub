import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str, logfile: str = "audio_hub.log") -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler (stderr)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rotating file handler
    Path(logfile).parent.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(logfile, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
