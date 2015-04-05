import time

_config_ = {
        'timeout': 3,
        'noparallel': True
        }

def test():
    for i in range(0, 6):
        time.sleep(1)
