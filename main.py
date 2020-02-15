import uart
from threading import *
from bitarray import *
import time
import wiringpi
from ChessBoard import ChessBoard
import atexit
import screen
import RPi.GPIO as gpio
import pickle
from collections import Counter
from copy import copy
import subprocess
import signal


class Settings:
    def __init__(self):
        self.inactivePeriod = 15  # Timer until the backlight turns off
        self.blackTime = 6
        self.whiteTime = 130
        self.assistLevel = 2
        self.chargeOutput = "%"
        self.timePunishment = " ON"
        self.difficulty = 0
        self.mode = "COMPUTER"
        self.computerColor = "BLACK"
        self.isChanged = False


try:
    file = open("settings.brd", 'rb')
    curSettings = pickle.load(file)
    file.close()
except:
    curSettings = Settings()
    print("Reading failed")

virtBrd = ChessBoard()
screenClass = screen.Screen(curSettings.inactivePeriod, curSettings.whiteTime, curSettings.blackTime,
                            curSettings.timePunishment, curSettings.chargeOutput)
pins = [13, 19, 20, 21]  # x,ok,right,left
loader = {"p": "Put black pawn", "k": "Put black king", "r": "Put black rook", "b": "Put black bishop",
          "q": "Put black queen", "n": "Put black knight", "P": "Put white pawn", "K": "Put white king",
          "R": "Put white rook", "B": "Put white bishop", "Q": "Put white queen", "N": "Put white knight"}


class Movements:
    engine = subprocess.Popen(
        '/usr/games/stockfish',
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, bufsize=1, close_fds=True)
    taken = tuple()
    enemyTaken = tuple()
    taketime = 0
    gameOver = -1
    movesShown = False
    isPressed = 0
    gameStarted = False
    gameToStart = False
    promotionList = list()


class scrn(Thread):
    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name

    def run(self):
        while isRunning:
            try:
                screenClass.RunThread(uart.ScreenArray, Movements.taken, curSettings)
                if screenClass.haveToDump:
                    dumpGame()
                    screenClass.haveToDump = False
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
                        screenClass.curHint = ''
                        uart.ScreenArray.errorState = 0
                        screenClass.timerActive = False
                        Movements.enemyTaken = tuple()
                        Movements.Taken = tuple()
                        Movements.promotionList = list()
                        Movements.taketime = 0
                        initEngine()
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
    Movements.promotionList = list()
    screenClass.curHint = ''
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
    initEngine()


def SPISend(buf):
    wiringpi.wiringPiSPIDataRW(0, buf)
    wiringpi.pinMode(1, 1)  # Set pin 6 to 1 ( OUTPUT )
    wiringpi.digitalWrite(1, 1)  # Write 1 ( HIGH ) to pin 6
    time.sleep(0.000001)
    wiringpi.digitalWrite(1, 0)  # Write 1 ( HIGH ) to pin 6


def interfaceGameStartEvent():
    uart.ScreenArray.gameState = 1
    virtBrd.resetBoard()
    initEngine()
    Movements.gameStarted = True
    screenClass.curHint = ''
    showErrorAction()
    if Movements.gameStarted:
        gameStartAction()
        if curSettings.mode == "COMPUTER" and \
                (curSettings.computerColor == "WHITE" or curSettings.computerColor == " BOTH"):
            uart.ScreenArray.gameState = 12
            handleComputerMoveAction()
        else:
            uart.ScreenArray.gameState = 2


def gameStartAction():
    singleBlink(parseExistance(virtBrd.getBoard()))
    pass  # Start the game by blinking all not empty boxes once


def singleBlink(coordsList, duration=0.4):
    LedUpdate(coordsList)
    time.sleep(duration)
    LedUpdate([])
    pass  # Blink LEDs once


def dumpGame():
    moves = virtBrd.getAllTextMoves(0)
    try:
        file = open("Saved game.brd", 'wb')
        pickle.dump((moves, Movements.promotionList), file)
        file.close()
    except:
        print("Saving failed")


def get():
    # using the 'isready' command (engine has to answer 'readyok')
    # to indicate current last line of stdout
    stx = ""
    Movements.engine.stdin.write('isready\n')
    print('\nengine:')
    while True:
        text = Movements.engine.stdout.readline().strip()
        # text = engine.communicate()[0].strip()
        if text == 'readyok':
            break
        if text != '':
            print(('\t' + text))
        if text[0:8] == 'bestmove':
            return text


def put(command):
    print(('\nyou:\n\t' + command))
    Movements.engine.stdin.write(command + '\n')


def sget():
    # using the 'isready' command (engine has to answer 'readyok')
    # to indicate current last line of stdout
    stx = ""
    Movements.engine.stdin.write('isready\n')
    print('\nengine:')
    while True:
        text = Movements.engine.stdout.readline().strip()
        # if text == 'readyok':
        #   break
        if not Movements.gameStarted:
            return ''
        if text != '':
            print(('\t' + text))
        if text[0:8] == 'bestmove':
            mtext = text
            return mtext


def initEngine():
    Movements.engine.send_signal(signal.SIGINT)
    Movements.engine.communicate()
    Movements.engine = subprocess.Popen(
        '/usr/games/stockfish',
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, bufsize=1, close_fds=True)
    get()
    put('uci')
    get()
    put('setoption name Skill Level value ' + str(curSettings.difficulty))
    get()
    put('setoption name Hash value 128')
    get()
    put("setoption name Threads value 4")
    get()
    put('uci')
    get()
    put('ucinewgame')


def parseBoardUpdate(board, last):
    if screenClass.paused:
        showErrorAction(True)
    else:
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
    if curSettings.assistLevel >= 1:
        LedUpdate(virtBrd.getValidMoves(coords))
    Movements.movesShown = True


def onFigureTakenEvent(coords):
    showMoves(coords)
    Movements.taken = coords
    Movements.taketime = time.perf_counter()
    pass  # show all available directions, store the address


def onFigurePlacedEvent(coords):
    singleBlink([coords])
    if ((coords[1] == 0 and virtBrd.getColor(Movements.taken[0], Movements.taken[1]) == virtBrd.WHITE) or
        (coords[1] == 7 and virtBrd.getColor(Movements.taken[0], Movements.taken[1]) == virtBrd.BLACK)) and \
            isPawn(virtBrd.getBoard(), Movements.taken):
        screenClass.toSetPromotion = True
        while screenClass.promotion == 0:
            time.sleep(0.1)
        virtBrd.setPromotion(screenClass.promotion)
        Movements.promotionList.append(screenClass.promotion)
        screenClass.promotion = 0
    if not virtBrd.addMove(Movements.taken, coords):
        rsn = virtBrd.getReason()
        print("REASON = " + str(rsn))
        uart.ScreenArray.errorState = rsn
        showErrorAction(True)
    else:
        screenClass.curHint = ''
        Movements.taken = tuple()
        Movements.enemyTaken = tuple()
        Movements.movesShown = False
        showErrorAction()
        parseGameState()
    pass  # check if the move is legit (ask the engine or virtual board), make this damn move


def parseGameState():
    game_end = virtBrd.getGameResult()
    gameState = 0
    if not virtBrd.isGameOver():
        if virtBrd.isCheck():
            if virtBrd.getTurn() == virtBrd.WHITE:
                gameState = 4
            else:
                gameState = 10
        elif virtBrd.getTurn() == virtBrd.WHITE:
            gameState = 2
        else:
            gameState = 3
    elif game_end == 1:
        gameState = 5
    elif game_end == 2:
        gameState = 6
    elif game_end == 3:
        gameState = 7
    elif game_end == 4:
        gameState = 8
    elif game_end == 5:
        gameState = 9
    checkForBotTurn(gameState)


def checkForBotTurn(gameState):
    if curSettings.mode == "COMPUTER":
        if (gameState == 4 or gameState == 2) \
                and (curSettings.computerColor == "WHITE" or curSettings.computerColor == " BOTH"):
            uart.ScreenArray.gameState = 12
            handleComputerMoveAction()
        elif (gameState == 10 or gameState == 3) \
                and (curSettings.computerColor == "BLACK" or curSettings.computerColor == " BOTH"):
            uart.ScreenArray.gameState = 12
            handleComputerMoveAction()
        else:
            uart.ScreenArray.gameState = gameState
    else:
        uart.ScreenArray.gameState = gameState


def isPawn(brdModel, coords):
    if brdModel[coords[1]][coords[0]].upper() == "P":
        return True
    else:
        return False


def parseExistance(brdModel, filter=''):
    parsed = list()
    for j in range(8):
        for i in range(8):
            if filter == '':
                if brdModel[j][i] != '.':
                    parsed.append((i, j))
            elif brdModel[j][i] == filter:
                parsed.append((i, j))
    return parsed


def showErrorAction(keepTaken=False, customgoal=None):
    if customgoal != None:
        goal = customgoal
    else:
        goal = parseExistance(virtBrd.getBoard())
    if keepTaken and len(Movements.taken) == 2:
        goal.remove(Movements.taken)
    startTimer = time.perf_counter()
    emitPeriod = 0.3
    waitPeriod = 0.5
    curState = False
    while not compare(goal, uart.Array.brdArray):
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
        curTime = curTimer - startTimer
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


def findMovesForEngine():
    moves = virtBrd.getAllTextMoves(0)
    result = ''
    promotions = copy(Movements.promotionList)
    tempBrd = ChessBoard()
    tempBrd.resetBoard()
    if moves != None:
        for i in moves:
            result += " "
            result += i
            if not tempBrd.addTextMove(i):
                if tempBrd.getReason() == 5:
                    promote = promotions.pop(0)
                    tempBrd.setPromotion(promote)
                    if not tempBrd.addTextMove(i):
                        print("Promote failed")
                        return ''
                    if promote == 1:
                        result += "q"
                    elif promote == 2:
                        result += "r"
                    elif promote == 3:
                        result += "n"
                    elif promote == 4:
                        result += "b"
                else:
                    print("Failed")
                    return ''
            tempBrd.setPromotion(0)
    return "position startpos moves" + result


def handleComputerMoveAction():
    screenClass.toShow = "Please wait..."
    screenClass.noBlink = True
    cmove = findMovesForEngine()
    print(cmove)
    put(cmove)
    if curSettings.computerColor == "WHITE":
        put("go movetime " + str(curSettings.whiteTime * 1000))
    else:
        put("go movetime " + str(curSettings.blackTime * 1000))
    text = sget()
    if Movements.gameStarted:
        print(text)
        Movements.taken = textToCoords(text[9:11])
        Movements.taketime = 2
        place = textToCoords(text[11:13])
        if len(text) > 13:
            if text[13] != ' ':
                screenClass.curHint = text[22:26]
                if text[13] == 'q':
                    virtBrd.setPromotion(1)
                    screenClass.toShow = "QUEEN PROMOTION"
                    Movements.promotionList.append(1)
                elif text[13] == 'b':
                    virtBrd.setPromotion(4)
                    screenClass.toShow = "BISHOP PROMOTION"
                    Movements.promotionList.append(4)
                elif text[13] == 'n':
                    virtBrd.setPromotion(3)
                    screenClass.toShow = "KNIGHT PROMOTION"
                    Movements.promotionList.append(3)
                elif text[13] == 'r':
                    virtBrd.setPromotion(2)
                    screenClass.toShow = "ROOK PROMOTION"
                    Movements.promotionList.append(2)
            else:
                screenClass.curHint = text[21:25]
                screenClass.toShow = "Follow the guide"
        else:
            screenClass.curHint = ''
            screenClass.toShow = "Follow the guide"
        if not virtBrd.addMove(Movements.taken, place):
            rsn = virtBrd.getReason()
            print("REASON = " + str(rsn))
            uart.ScreenArray.errorState = rsn
            parseGameState()
        else:
            moveFigures(Movements.taken, place)
            showErrorAction()
            Movements.taken = tuple()
            Movements.enemyTaken = tuple()
            parseGameState()
            screenClass.toShow = ""
            screenClass.lastShown = ""
            parseGameState()
    else:
        screenClass.toShow = ""
        screenClass.lastShown = ""
        Movements.taken = tuple()
        Movements.enemyTaken = tuple()
    pass  # guide the player to move figure


def moveFigures(take, place):
    singleBlink([take])
    guideTake(take)
    if place in uart.Array.brdArray:
        guideTake(place)
    singleBlink([place])
    guidePlace(place)
    time.sleep(0.15)
    singleBlink([place], duration=0.1)


def guideTake(target):
    startTimer = time.perf_counter()
    emitPeriod = 0.2
    waitPeriod = 0.2
    curState = False
    while target in uart.Array.brdArray:
        if Movements.gameOver != -1:
            break
        if not Movements.gameStarted:
            break
        curTimer = time.perf_counter()
        curTime = curTimer - startTimer
        if curState and curTime > emitPeriod:
            LedUpdate([])
            curState = False
            startTimer = curTimer
        elif not curState and curTime > waitPeriod:
            LedUpdate([target])
            curState = True
            startTimer = curTimer
        time.sleep(0.01)


def guidePlace(target):
    LedUpdate([target])
    while target not in uart.Array.brdArray:
        if Movements.gameOver != -1:
            break
        if not Movements.gameStarted:
            break
        time.sleep(0.01)
    LedUpdate([])


def textToCoords(string):
    return ord(string[0]) - 97, 8 - int(string[1])


def onPress(channel):
    if not gpio.input(channel):
        timer = time.perf_counter()
        while not gpio.input(channel):
            time.sleep(0.2)
        uart.ScreenArray.button = (channel, time.perf_counter() - timer)
        print(uart.ScreenArray.button)


def interfaceGameLoadEvent():
    screenClass.curHint = ''
    try:
        file = open("Saved game.brd", 'rb')
        info = pickle.load(file)
        movements = info[0]
        Movements.promotionList = info[1]
        promotions = copy(info[1])
        file.close()
    except:
        uart.ScreenArray.gameState = 0
        print("Reading failed")
        return
    virtBrd.resetBoard()
    initEngine()
    for i in movements:
        if not virtBrd.addTextMove(i):
            if virtBrd.getReason() == 5:
                virtBrd.setPromotion(promotions.pop(0))
                if not virtBrd.addTextMove(i):
                    print("Promote failed")
                    uart.ScreenArray.gameState = 0
                    return
            else:
                print("Restore failed")
                uart.ScreenArray.gameState = 0
                return
        virtBrd.setPromotion(0)
    uart.ScreenArray.gameState = 11
    screenClass.gameStarted = True
    Movements.gameStarted = True
    goal = list()
    for i in loader:
        screenClass.toShow = loader[i]
        goal.extend(parseExistance(virtBrd.getBoard(), filter=i))
        showErrorAction(customgoal=goal)
    showErrorAction()
    if Movements.gameStarted:
        gameStartAction()
        if not virtBrd.isCheck():
            gameState = virtBrd.getTurn() + 2
        else:
            if virtBrd.getTurn() == 0:
                gameState = 4
            else:
                gameState = 10
        checkForBotTurn(gameState)
    screenClass.toShow = ''
    screenClass.lastShown = ''


def compare(s, t):
    return Counter(s) == Counter(t)


def updateSettings(settings):
    screenClass.inactiveTime = settings.inactivePeriod
    screenClass.blackTime = settings.blackTime
    screenClass.punish = settings.timePunishment
    screenClass.charge = settings.chargeOutput
    screenClass.whiteTime = settings.whiteTime
    try:
        file = open("settings.brd", 'wb')
        pickle.dump(settings, file)
        file.close()
    except:
        print("Saving failed")


def useHint():
    takeCoords = textToCoords(screenClass.curHint[:2])
    placeCoords = textToCoords(screenClass.curHint[2:4])
    Movements.movesShown = False
    showErrorAction()
    if ((placeCoords[1] == 0 and virtBrd.getColor(takeCoords[0], takeCoords[1]) == virtBrd.WHITE) or
        (placeCoords[1] == 7 and virtBrd.getColor(takeCoords[0], takeCoords[1]) == virtBrd.BLACK)) and \
            isPawn(virtBrd.getBoard(), takeCoords):
        screenClass.toSetPromotion = True
        while screenClass.promotion == 0:
            time.sleep(0.1)
        virtBrd.setPromotion(screenClass.promotion)
        Movements.promotionList.append(screenClass.promotion)
        screenClass.promotion = 0
    if not virtBrd.addMove(takeCoords, placeCoords):
        rsn = virtBrd.getReason()
        print("REASON = " + str(rsn))
        uart.ScreenArray.errorState = rsn
        showErrorAction(True)
    else:
        moveFigures(takeCoords, placeCoords)
        screenClass.hintUsed = False
        parseGameState()


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
        if screenClass.hintUsed:
            useHint()
        if screenClass.haveToLoad:
            interfaceGameLoadEvent()
            screenClass.haveToLoad = False
        if uart.Array.brdArray != uart.Array.lastShown and Movements.gameStarted:
            # LedUpdate(uart.Array.brdArray)  # Uncomment to test Magnets
            parseBoardUpdate(uart.Array.brdArray, uart.Array.lastShown)
            uart.Array.lastShown = uart.Array.brdArray
        time.sleep(0.01)
except:
    onDisposeEvent()
    isRunning = False
# TODO FAR: blitz mode (maybe)
