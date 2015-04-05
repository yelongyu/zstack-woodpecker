import time
import random

_config_ = {
        'timeout': 10,
        'noparallel': False
        }

def test():
    for i in range(0, random.randrange(2,5,1)):
        time.sleep(1)
    
    i = random.choice([0,1])

    if i:
        raise "ERROR"
