import time
from zstacklib.utils import log

logger = log.get_logger(__name__)

def test():
    for i in range(0, 5):
        logger.debug(i)
        time.sleep(2)
