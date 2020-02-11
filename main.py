import uart
from threading import *
from bitarray import *
import time
import wiringpi


class brd(Thread):
    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name

    def run(self):
        while isRunning:
            try:
                uart.RunThread()
            except:
                pass


def LedUpdate(list1):
    x = bitarray(8 * 8)
    x.setall(False)
    for i in list1:
        if (i[0] % 2 == 1):
            id = i[0] * 8 + i[1]
        else:
            id = i[0] * 8 + (7 - i[1])
        x[id] = 1
    SPISend(x.tobytes())
    uart.LEblink()


def SPISend(buf):
    retlen, retdata = wiringpi.wiringPiSPIDataRW(0, buf)
    wiringpi.pinMode(1, 1)  # Set pin 6 to 1 ( OUTPUT )
    wiringpi.digitalWrite(1, 1)  # Write 1 ( HIGH ) to pin 6
    time.sleep(0.000001)
    wiringpi.digitalWrite(1, 0)  # Write 1 ( HIGH ) to pin 6


def interfaceGameStartEvent():
    if not uart.Board_Ready:
        pass  # blink with wrong boxes
    else:
        gameStartAction()


def gameStartAction():
    pass  # Start the game by blinking all not empty boxes once


def boardUpdatedCallback(list):
    if not uart.Board_Ready:
        pass  # Highlight the missing boxes and blink with false positive boxes
    else:
        gameStartAction()


def parseBoardUpdate():
    pass  # check what actually had changed on the board; if new figures - make sure that there are no overlaps.


def onFigureTakenEvent():
    pass  # show all available directions, store the address


def onGameStartedEvent():
    pass  # check if all figures are ready; start the engine


def onFigurePlacedEvent():
    pass  # check if the move is legit (ask the engine or virtual board), make this damn move


def showErrorAction(list):
    pass  # blink with the right box if the move is wrong


def handleComputerMoveAction():
    pass  # guide the player to move figure


isRunning = True
boardComm = brd("Board")
boardComm.start()
wiringpi.wiringPiSetup()
wiringpi.wiringPiSPISetup(0, 27000000)
while True:
    if uart.Array.brdArray != uart.Array.lastShown:
        LedUpdate(uart.Array.brdArray)
        uart.Array.lastShown = uart.Array.brdArray
isRunning = False
# TODO: Add a dedicated thread for interface handling (difficulty, side, start functionality for now)
# TODO future: interface features: number of players, timer, hints, blitz mode (maybe)
# TODO 3: Refactor UART comm (all reading move to a dedicated thread with notify() on receive "ok\r\n")
