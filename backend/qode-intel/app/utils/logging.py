import logging
import sys

from app.config import LOG_LEVEL

LEVEL = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("qode-intel")
