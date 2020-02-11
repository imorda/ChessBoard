import wiringpi
import time
from bitarray import *

def LedUpdate(list1):
    x = bitarray(8 * 8)
    x.setall(False)
    for i in list1:
        if (i[0] % 2 == 1):
            id = i[0] * 8 + i[1]
        else:
            id = i[0] * 8 + (7 - i[1])
        x[id] = 1
    return x.tobytes()



buf = LedUpdate([[4,5]])

