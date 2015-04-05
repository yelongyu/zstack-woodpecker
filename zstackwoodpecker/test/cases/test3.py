import time
from zstacklib.utils import log

logger = log.get_logger(__name__)

def test():
    time.sleep(3)
    raise Exception('on purpose')
