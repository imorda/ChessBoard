import uart
from threading import *
from bitarray import *
import time
import wiringpi
from ChessBoard import ChessBoard
import atexit
import screen
import RPi.GPIO as gpio


class Settings:
    inactivePeriod = 0  # Timer until the backlight turns off
    blackTime = 120
    whiteTime = 120
    assistLevel = 1
    chargeOutput = "V"
    timePunishment = " ON"
    difficulty = 1
    mode = "  PLAYER"
    computerColor = "BLACK"
    isChanged = False


curSettings = Settings
virtBrd = ChessBoard()
screenClass = screen.Screen(curSettings.inactivePeriod, curSettings.whiteTime, curSettings.blackTime,
                            curSettings.timePunishment, curSettings.chargeOutput)
pins = [13,19,20,21]  # x,ok,right,left


class Movements:
    taken = tuple()
    enemyTaken = tuple()
    taketime = 0
    gameOver = -1
    movesShown = False
    isPressed = 0
    gameStarted = False
    gameToStart = False


class scrn(Thread):
    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name

    def run(self):
        while isRunning:
            try:
                screenClass.RunThread(uart.ScreenArray, Movements.taken, curSettings)
                if screenClass.gameOver != -1:
                    Movements.gameOver = screenClass.gameOver
                elif screenClass.gameStarted:
                    if uart.ScreenArray.gameState == 0:
                        Movements.gameToStart = True
                else:
                    if uart.ScreenArray.gameState != 0:
                        Movements.gameStarted = False
                        uart.ScreenArray.gameState = 0
                        Movements.movesShown = False
                        uart.ScreenArray.errorState = 0
                        screenClass.timerActive = False
                        Movements.enemyTaken = tuple()
                        Movements.Taken = tuple()
                        Movements.taketime = 0
                        LedUpdate([])
                time.sleep(0.9)
            except:
                pass


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


def highlightWinner(color):
    uart.ScreenArray.gameState = -1
    uart.ScreenArray.errorState = 0
    screenClass.timerActive = False
    screenClass.gameOver = -1
    Movements.taken = tuple()
    Movements.gameOver = -1
    Movements.enemyTaken = tuple()
    Movements.taketime = 0
    Movements.movesShown = False
    toHighlight = list()
    if 0 <= color <= 1:
        for i in uart.Array.brdArray:
            if virtBrd.getColor(i[0], i[1]) == color:
                toHighlight.append(i)
    else:
        toHighlight = uart.Array.brdArray
    for i in range(2):
        LedUpdate(toHighlight)
        time.sleep(3)
        LedUpdate([])
        time.sleep(3)
    uart.ScreenArray.gameState = 0
    Movements.gameStarted = False
    screenClass.gameStarted = False


def SPISend(buf):
    wiringpi.wiringPiSPIDataRW(0, buf)
    wiringpi.pinMode(1, 1)  # Set pin 6 to 1 ( OUTPUT )
    wiringpi.digitalWrite(1, 1)  # Write 1 ( HIGH ) to pin 6
    time.sleep(0.000001)
    wiringpi.digitalWrite(1, 0)  # Write 1 ( HIGH ) to pin 6


def interfaceGameStartEvent():
    uart.ScreenArray.gameState = 1
    virtBrd.resetBoard()
    Movements.gameStarted = True
    showErrorAction()
    if Movements.gameStarted:
        gameStartAction()
        uart.ScreenArray.gameState = 2


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
                if friendly and len(virtBrd.getValidMoves(i)) > 0:
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


def showMoves(coords):
    if Settings.assistLevel >= 1:
        LedUpdate(virtBrd.getValidMoves(coords))
    Movements.movesShown = True


def onFigureTakenEvent(coords):
    showMoves(coords)
    Movements.taken = coords
    Movements.taketime = time.perf_counter()
    pass  # show all available directions, store the address


def onFigurePlacedEvent(coords):
    singleBlink([coords])
    if ((coords[1] == 0 and virtBrd.getColor(Movements.taken[0],Movements.taken[1]) == virtBrd.WHITE) or
        (coords[1] == 7 and virtBrd.getColor(Movements.taken[0],Movements.taken[1]) == virtBrd.BLACK)) and \
            isPawn(virtBrd.getBoard(), Movements.taken):
        screenClass.setPromotion()
        while screenClass.promotion == 0:
            time.sleep(0.1)
        virtBrd.setPromotion(screenClass.promotion)
        screenClass.promotion = 0
    if not virtBrd.addMove(Movements.taken, coords):
        rsn = virtBrd.getReason()
        print("REASON = " + str(rsn))
        uart.ScreenArray.errorState = rsn
        showErrorAction(True)
    else:
        Movements.taken = tuple()
        Movements.enemyTaken = tuple()
        Movements.movesShown = False
        parseGameState()
    pass  # check if the move is legit (ask the engine or virtual board), make this damn move


def parseGameState():
    game_end = virtBrd.getGameResult()
    if not virtBrd.isGameOver():
        if virtBrd.isCheck():
            if virtBrd.getTurn() == virtBrd.WHITE:
                uart.ScreenArray.gameState = 4
            else:
                uart.ScreenArray.gameState = 10
        elif virtBrd.getTurn() == virtBrd.WHITE:
            uart.ScreenArray.gameState = 2
        else:
            uart.ScreenArray.gameState = 3
    elif game_end == 1:
        uart.ScreenArray.gameState = 5
    elif game_end == 2:
        uart.ScreenArray.gameState = 6
    elif game_end == 3:
        uart.ScreenArray.gameState = 7
    elif game_end == 4:
        uart.ScreenArray.gameState = 8
    elif game_end == 5:
        uart.ScreenArray.gameState = 9


def isPawn(brdModel, coords):
    if brdModel[coords[1]][coords[0]].upper() == "P":
        return True
    else:
        return False


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
        if Movements.gameOver != -1:
            break
        if not Movements.gameStarted:
            break
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
        time.sleep(0.01)
    if not keepTaken:
        Movements.taken = tuple()
    Movements.enemyTaken = tuple()
    if not Movements.movesShown:
        LedUpdate([])
    else:
        showMoves(Movements.taken)
    pass  # blink with the right box if the move is wrong


def handleComputerMoveAction():
    pass  # guide the player to move figure


def onPress(channel):
    if not gpio.input(channel):
        timer = time.perf_counter()
        while not gpio.input(channel):
            time.sleep(0.2)
        uart.ScreenArray.button = (channel, time.perf_counter() - timer)
        print(uart.ScreenArray.button)


def updateSettings(settings):
    screenClass.inactiveTime = settings.inactivePeriod
    #settings.computerColor
    screenClass.blackTime = settings.blackTime
    #settings.difficulty
    screenClass.punish = settings.timePunishment
    screenClass.charge = settings.chargeOutput
    screenClass.whiteTime = settings.whiteTime
    #settings.mode


def onDisposeEvent():
    print("Shutting down...")
    LedUpdate([])
    gpio.cleanup()


atexit.register(onDisposeEvent)
isRunning = True
try:
    boardComm = brd("Board")
    boardComm.start()
    scrnThread = scrn("Screen")
    scrnThread.start()
    gpio.setmode(gpio.BCM)
    for i in pins:
        gpio.setup(i, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(i, gpio.FALLING, callback=onPress, bouncetime=50)
    wiringpi.wiringPiSetup()
    wiringpi.wiringPiSPISetup(0, 27000000)
    uart.Array.lastShown = uart.Array.brdArray
    LedUpdate([])
    while True:
        if Movements.gameOver != -1:
            highlightWinner(Movements.gameOver)
        if Movements.gameToStart:
            interfaceGameStartEvent()
            Movements.gameToStart = False
        if curSettings.isChanged and screenClass.curScreen == 0:
            updateSettings(curSettings)
            curSettings.isChanged = False
        if uart.Array.brdArray != uart.Array.lastShown and Movements.gameStarted:
            # LedUpdate(uart.Array.brdArray)  # Uncomment to test Magnets
            parseBoardUpdate(uart.Array.brdArray, uart.Array.lastShown)
            uart.Array.lastShown = uart.Array.brdArray
        time.sleep(0.01)
except:
    onDisposeEvent()
    isRunning = False
# TODO: Interface (settings restore, game restore)
# TODO 2: STOCKFISH, HINT SHOW
# TODO FAR: blitz mode (maybe)
