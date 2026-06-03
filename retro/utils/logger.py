import logging
import sys

from retro.core.config import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, config.logging.level.upper(), logging.INFO)
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
