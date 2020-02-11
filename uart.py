import RPi.GPIO as gpio
import time
import serial
from bitarray import *

gpio.setmode(gpio.BCM)
LEpino_Arduino = 18
gpio.setup(LEpino_Arduino, gpio.OUT)
time.sleep(0.15)
gpio.output(LEpino_Arduino, gpio.LOW)

ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
)


class Array:
    brdArray = list()
    lastShown = list()


def RunThread():
        x=ser.readline().replace(b'\r\n',b'')
        print(x)
        Parse(x)


def LEblink():
        gpio.output(LEpino_Arduino, gpio.HIGH)
        time.sleep(0.001)
        gpio.output(LEpino_Arduino, gpio.LOW)


def Parse(x = b''):
        if x.startswith(b"FU"):  # Figure update -> array of the board   -> to callback1
                value = bitarray()
                value.frombytes(x[2:])
                toShow = list()
                for i in range(len(value)):
                        if value[i] == 1:
                                toShow.append([i % 8, i // 8])
                Array.brdArray = toShow
                ser.write(b"ok2\n")