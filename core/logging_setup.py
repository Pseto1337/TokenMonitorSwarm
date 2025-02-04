# core/logging_setup.py
import logging
from core.config import settings

def setup_logging(log_level="DEBUG"):
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Logging is set up.")
