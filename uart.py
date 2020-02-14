import serial
from bitarray import *

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
)


class Array:
    brdArray = list()
    lastShown = list()


class ScreenArray:
    voltage = float()
    isCharging = bool()
    button = (0, 0)  # pin, duration
    # Button pin map:
    # 13 - x
    # 19 - ok
    # 20 - right
    # 21 - left
    errorState = 0
    gameState = 0
    # GAME STATE:
    # 0 - idle!
    # 1 - initializing!
    # 2 - white turn!
    # 3 - black turn!
    # 4 - check (white turn) !
    # 5 - white win!
    # 6 - black win!
    # 7 - draw (stalemate)!
    # 8 - draw (50 moves rule)!
    # 9 - draw (3 repetitions rule)!
    # 10 - check (black turn)!


def RunThread():
    x = ser.readline().replace(b'\r\n', b'')
    print(x)
    Parse(x)


def Parse(x=b''):
    if x == b"FU":  # Figure update -> array of the board   -> to callback1
        y = ser.read(8)
        if len(y) == 8 and ser.readline() == b'\r\n':
            print(y)
            value = bitarray()
            value.frombytes(y)
            to_show = list()
            for i in range(len(value)):
                if value[i] == 1:
                    to_show.append((i % 8, i // 8))
            Array.brdArray = to_show
            ser.write(b"ok\n")
    elif x.startswith(b"BU"):
        ScreenArray.voltage = float(x[3:])
        ScreenArray.isCharging = (x[2] == 67)
        ser.write(b"ok\n")
