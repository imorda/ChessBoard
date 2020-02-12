import uart
from threading import *
from bitarray import *
import time
import wiringpi
from ChessBoard import ChessBoard
import atexit

virtBrd = ChessBoard()


class Movements:
    taken = tuple()
    enemyTaken = tuple()
    taketime = 0


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
        if i[0] % 2 == 1:
            id = i[0] * 8 + (7 - i[1])
        else:
            id = i[0] * 8 + i[1]
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
    showErrorAction()
    gameStartAction()


def gameStartAction():
    singleBlink(parseExistance(virtBrd.getBoard()))
    pass  # Start the game by blinking all not empty boxes once


def singleBlink(coordsList):
    LedUpdate(coordsList)
    time.sleep(0.7)
    LedUpdate([])
    pass  # Blink LEDs once


def parseBoardUpdate(board, last):
    for i in last:
        if i not in board:
            friendly = (virtBrd.getColor(i[0], i[1]) == virtBrd.getTurn())
            if len(Movements.taken) == 0:
                if friendly:
                    onFigureTakenEvent(i)
                else:
                    showErrorAction()
            elif not friendly:
                Movements.enemyTaken = i
            else:
                showErrorAction(True)


    for i in board:
        if i not in last and len(last) > 0:
            if len(Movements.taken) == 0:
                showErrorAction()
            elif i == Movements.taken:
                if time.perf_counter() - Movements.taketime > 1:
                    showErrorAction(True)
            else:
                onFigurePlacedEvent(i)
            pass  # check what actually had changed on the board; if new figures - make sure that there are no overlaps.


def onFigureTakenEvent(coords):
    LedUpdate(virtBrd.getValidMoves(coords))
    Movements.taken = coords
    Movements.taketime = time.perf_counter()
    pass  # show all available directions, store the address


def onFigurePlacedEvent(coords):
    singleBlink([coords])
    if not virtBrd.addMove(Movements.taken, coords):
        print("REASON = " + str(virtBrd.getReason()))
        showErrorAction(True)
    else:
        Movements.taken = tuple()
        Movements.enemyTaken = tuple()
    pass  # check if the move is legit (ask the engine or virtual board), make this damn move


def parseExistance(brdModel):
    parsed = list()
    for j in range(8):
        for i in range(8):
            if brdModel[j][i] != '.':
                parsed.append((i,j))
    return parsed

def showErrorAction(keepTaken = False):
    goal = parseExistance(virtBrd.getBoard())
    if keepTaken:
        goal.remove(Movements.taken)
    startTimer = time.perf_counter()
    emitPeriod = 0.3
    waitPeriod = 0.5
    curState = False
    while goal != uart.Array.brdArray:
        curTimer = time.perf_counter()
        toBlink = list()
        for i in goal:
            if i not in uart.Array.brdArray:
                toBlink.append(i)
        for i in uart.Array.brdArray:
            if i not in goal:
                toBlink.append(i)
        curTime = curTimer-startTimer
        if curState and curTime > emitPeriod:
            LedUpdate([])
            curState = False
            startTimer = curTimer
        elif not curState and curTime > waitPeriod:
            LedUpdate(toBlink)
            waitPeriod = 1
            curState = True
            startTimer = curTimer
    if not keepTaken:
        Movements.taken = tuple()
    Movements.enemyTaken = tuple()
    LedUpdate([])
    pass  # blink with the right box if the move is wrong


def handleComputerMoveAction():
    pass  # guide the player to move figure


def onDisposeEvent():
    print("Shutting down...")
    LedUpdate([])


atexit.register(onDisposeEvent)
isRunning = True
try:
    virtBrd.resetBoard()
    boardComm = brd("Board")
    boardComm.start()
    wiringpi.wiringPiSetup()
    wiringpi.wiringPiSPISetup(0, 27000000)
    interfaceGameStartEvent()
    uart.Array.lastShown = uart.Array.brdArray
    while True:
        if uart.Array.brdArray != uart.Array.lastShown:
            # LedUpdate(uart.Array.brdArray)  # Uncomment to test Magnets
            parseBoardUpdate(uart.Array.brdArray, uart.Array.lastShown)
            uart.Array.lastShown = uart.Array.brdArray
except:
    onDisposeEvent()
    isRunning = False
# TODO: Add a dedicated thread for interface handling (difficulty, side, start functionality for now)
# TODO future: interface features: number of players, timer, hints, blitz mode (maybe)
