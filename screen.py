import I2C_LCD_driver
import time
import math
import os.path


def CalculateBatteryIcon(voltage):
    if voltage < 3.3:
        return 0
    elif 3.3 <= voltage < 3.48:
        return 1
    elif 3.48 <= voltage < 3.66:
        return 2
    elif 3.66 <= voltage < 3.84:
        return 3
    elif 3.84 <= voltage < 4.02:
        return 4
    elif 4.02 <= voltage < 4.15:
        return 5
    elif 4.15 <= voltage:
        return 6


class Screen:
    lcd = I2C_LCD_driver.lcd()
    inactiveTime = 60
    curScreen = 0
    promotion = 0
    dontReset = False
    drawn = False
    gameOver = -1
    lastBatteryIcon = -1
    lastChargingState = False
    hintUsed = False
    curTurn = 0
    lit = True
    timerEnd = 0
    paused = False
    punish = "OFF"
    curHint = ''
    selectedItem = None
    timerActive = False
    haveToLoad = False
    hintAvailable = False
    toPlay = 0
    charge = "%"
    toSetPromotion = False
    drawnState = -1
    whiteTime = 120
    takenDrawn = tuple()
    noBlink = False
    taken = tuple()
    menuPosition = 1
    lastPos = 1
    gameStarted = False
    lastClock = 0
    toShow = ''
    lastShown = ''
    blackTime = 6
    haveToDump = False
    lastActiveTime = time.perf_counter()
    customChars = [
        [0b01110,
         0b01010,
         0b10001,
         0b10001,
         0b10001,
         0b10001,
         0b10001,
         0b11111],
        [0b01110,
         0b01010,
         0b10001,
         0b10001,
         0b10001,
         0b10001,
         0b11111,
         0b11111],
        [0b01110,
         0b01010,
         0b10001,
         0b10001,
         0b10001,
         0b11111,
         0b11111,
         0b11111],
        [0b01110,
         0b01010,
         0b10001,
         0b10001,
         0b11111,
         0b11111,
         0b11111,
         0b11111],
        [0b01110,
         0b01010,
         0b10001,
         0b11111,
         0b11111,
         0b11111,
         0b11111,
         0b11111],
        [0b01110,
         0b01010,
         0b11111,
         0b11111,
         0b11111,
         0b11111,
         0b11111,
         0b11111],
        [0b01110,
         0b01110,
         0b11111,
         0b11111,
         0b11111,
         0b11111,
         0b11111,
         0b11111],
        [0b01111,
         0b01001,
         0b10010,
         0b10011,
         0b11001,
         0b01010,
         0b10100,
         0b11000]
    ]
    timeRange = list()
    for i in range(1, 10):
        timeRange.append(i)

    for i in range(10, 100, 5):
        timeRange.append(i)

    for i in range(100, 1000, 30):
        timeRange.append(i)
    timeRange.append(999)
    rangeList = [
        range(21),  # difficulty
        ["  PLAYER", "COMPUTER"],  # modes
        timeRange,  # whites time
        timeRange,  # blacks time
        range(3),  # assist level
        ["V", "%"],  # charge format
        [" ON", "OFF"],  # time punishment
        range(0, 1000, 15),  # inactive period
        ["BLACK","WHITE", " BOTH"],  # computer color
        [" ON", "OFF"]  # beep
    ]

    lcd.lcd_load_custom_chars(customChars)

    def __init__(self, inactiveTime = 60, whiteTime=120, blackTime=6, punish = "OFF", charge = "%"):
        self.whiteTime = whiteTime
        self.blackTime = blackTime
        self.inactiveTime = inactiveTime
        self.drawn = False
        self.lcd.backlight(True)
        self.lit = True
        self.punish = punish
        self.charge = charge

    def RunThread(self, screenInfo, taken, generalSettings):
        self.taken = taken
        self.brightnessController(screenInfo)
        if self.toSetPromotion:
            self.setPromotion()
        if self.curScreen == 0:  # dashboard
            if screenInfo.button[0] == 19:
                if screenInfo.button[1] < 1.2:
                    if not self.gameStarted:
                        self.gameStarted = True
                    else:
                        if (2 <= screenInfo.gameState <= 4 or screenInfo.gameState == 10) and not self.hintUsed:
                            self.paused = not self.paused
                        pass  # pause the game
                elif not self.gameStarted:
                    self.switchScreen(6)
                    pass  # restore last game (or show error screen)
                elif 2 <= screenInfo.gameState <= 4 or screenInfo.gameState == 10 or screenInfo.gameState == 12:
                    self.switchScreen(5)  # show dialog to save this game
            elif screenInfo.button[0] == 13:
                if screenInfo.gameState == 0:
                    self.switchScreen(3)
                    pass  # enter settings
                elif screenInfo.gameState == 1 or screenInfo.gameState == 11:
                    self.gameStarted = False
                else:
                    self.switchScreen(1)
                    pass  # show dialog to delete this game
            elif (screenInfo.button[0] == 20 or screenInfo.button[0] == 21) and screenInfo.button[1] >= 1.2 \
                    and self.hintAvailable:
                self.useHint()
            else:
                self.DrawHome(screenInfo, generalSettings)
                self.runClock(generalSettings)
        elif self.curScreen == 1:  # game delete dialog
            if not self.drawn:
                self.printDialog("Do you want to",1)
                self.printDialog("ERASE this game?",2)
                self.drawn = True
            if screenInfo.button[0] == 19:
                self.gameStarted = False
                self.paused = False
                self.switchScreen(0)
            elif screenInfo.button[0] == 13:
                self.dontReset = True
                self.switchScreen(0)
        elif self.curScreen == 2:  # promotion
            if not self.drawn:
                self.lcd.lcd_display_string(" Queen  Bishop~", 1)
                self.lcd.lcd_display_string("X Knight Rook OK", 2)
                self.drawn = True
            if screenInfo.button[0] == 19:
                self.promotion = 2
                self.switchScreen(0)
            elif screenInfo.button[0] == 13:
                self.promotion = 3
                self.switchScreen(0)
            elif screenInfo.button[0] == 20:
                self.promotion = 4
                self.switchScreen(0)
            elif screenInfo.button[0] == 21:
                self.promotion = 1
                self.switchScreen(0)
        elif self.curScreen == 3:  # menu
            self.DrawMenu(generalSettings)
            if screenInfo.button[0] == 20:
                if self.menuPosition < 10:
                    self.menuPosition += 1
                else:
                    self.menuPosition = 1
            elif screenInfo.button[0] == 21:
                if self.menuPosition > 1:
                    self.menuPosition -= 1
                else:
                    self.menuPosition = 10
            elif screenInfo.button[0] == 13:
                self.switchScreen(0)
            elif screenInfo.button[0] == 19:
                self.switchScreen(4)
        elif self.curScreen == 4:  # menu value change
            if not self.drawn:
                item = str(self.selectedItem[1][self.selectedItem[2]])
                self.lcd.lcd_display_string_pos(item, 2 - self.menuPosition % 2, 16 - len(item))
                self.drawn = True
            if screenInfo.button[0] == 21:
                self.lcd.lcd_clear()
                if self.selectedItem[2] > 0:
                    self.selectedItem[2] -= 1
                else:
                    self.selectedItem[2] = len(self.selectedItem[1]) - 1
                item = str(self.selectedItem[1][self.selectedItem[2]])
                self.lcd.lcd_display_string_pos(item, 2 - self.menuPosition % 2, 16 - len(item))
            elif screenInfo.button[0] == 20:
                self.lcd.lcd_clear()
                if self.selectedItem[2] < len(self.selectedItem[1]) - 1:
                    self.selectedItem[2] += 1
                else:
                    self.selectedItem[2] = 0
                item = str(self.selectedItem[1][self.selectedItem[2]])
                self.lcd.lcd_display_string_pos(item, 2 - self.menuPosition % 2, 16 - len(item))
            elif screenInfo.button[0] == 13:
                self.switchScreen(3)
            elif screenInfo.button[0] == 19:
                self.updateClass(generalSettings, self.selectedItem[1][self.selectedItem[2]])
                self.switchScreen(3)
        elif self.curScreen == 5:  # game save dialog
            if not self.drawn:
                self.printDialog("Do you want to",1)
                self.printDialog("save this game?",2)
                self.drawn = True
            if screenInfo.button[0] == 19:
                self.haveToDump = True
                self.paused = False
                self.gameStarted = False
                self.switchScreen(0)
            elif screenInfo.button[0] == 13:
                self.dontReset = True
                self.switchScreen(0)
        elif self.curScreen == 6:  # game load dialog
            if not self.drawn:
                if os.path.isfile('Saved game.brd'):
                    self.printDialog("Do you want to", 1)
                    self.printDialog("load last game?", 2)
                    self.drawn = True
                else:
                    self.printDialog("No saved",1)
                    self.printDialog("games found",2)
                    time.sleep(1)
                    self.switchScreen(0)
            if screenInfo.button[0] == 19:
                self.haveToLoad = True
                self.switchScreen(0)
            elif screenInfo.button[0] == 13:
                self.switchScreen(0)
        if screenInfo.button != (0, 0):
            self.lastActiveTime = time.perf_counter()
            screenInfo.button = (0, 0)

    def useHint(self):
        self.paused = False
        self.hintUsed = True
        self.hintAvailable = False
        self.setTurn(self.curTurn)

    def updateClass(self, settings, value):
        if self.menuPosition == 1:
            settings.difficulty = value
        elif self.menuPosition == 2:
            settings.mode = value
        elif self.menuPosition == 3:
            settings.whiteTime = value
        elif self.menuPosition == 4:
            settings.blackTime = value
        elif self.menuPosition == 5:
            settings.assistLevel = value
        elif self.menuPosition == 6:
            settings.chargeOutput = value
        elif self.menuPosition == 7:
            settings.timePunishment = value
        elif self.menuPosition == 8:
            settings.inactivePeriod = value
        elif self.menuPosition == 9:
            settings.computerColor = value
        elif self.menuPosition == 10:
            settings.beep = value
        settings.isChanged = True

    def DrawMenu(self, settings):
        if not self.drawn or self.lastPos != self.menuPosition:
            if self.menuPosition <= 2:
                self.lcd.lcd_display_string(f" Difficulty     ", 1)
                self.lcd.lcd_display_string(f" Mode   {settings.mode}", 2)
                diff = str(settings.difficulty)
                self.lcd.lcd_display_string_pos(diff, 1, 16 - len(diff))
            elif 2 < self.menuPosition <= 4:
                self.lcd.lcd_display_string(" Whites time    ", 1)
                self.lcd.lcd_display_string(" Blacks time    ", 2)
                whitetime = str(settings.whiteTime)
                blacktime = str(settings.blackTime)
                self.lcd.lcd_display_string_pos(whitetime, 1, 16 - len(whitetime))
                self.lcd.lcd_display_string_pos(blacktime, 2, 16 - len(blacktime))
            elif 4 < self.menuPosition <= 6:
                self.lcd.lcd_display_string(f" Assist level  {settings.assistLevel}", 1)
                self.lcd.lcd_display_string(f" Charge format {settings.chargeOutput}", 2)
            elif 6 < self.menuPosition <= 8:
                self.lcd.lcd_display_string(f" Limit time  {settings.timePunishment}", 1)
                self.lcd.lcd_display_string(" AFK time       ", 2)
                afktime = str(settings.inactivePeriod)
                self.lcd.lcd_display_string_pos(afktime, 2, 16 - len(afktime))
            elif 8 < self.menuPosition <= 10:
                self.lcd.lcd_display_string(f" Bot color {settings.computerColor}", 1)
                self.lcd.lcd_display_string(f" Sounds      {settings.beep}", 2)
            self.lcd.lcd_display_string("*", 2 - self.menuPosition % 2)
            itemAssignment = [
                settings.difficulty,
                settings.mode,
                settings.whiteTime,
                settings.blackTime,
                settings.assistLevel,
                settings.chargeOutput,
                settings.timePunishment,
                settings.inactivePeriod,
                settings.computerColor,
                settings.beep
            ]
            index = self.rangeList[self.menuPosition-1].index(itemAssignment[self.menuPosition-1])
            self.selectedItem = [None, self.rangeList[self.menuPosition-1], index]
            self.lastPos = self.menuPosition
            self.drawn = True

    def switchScreen(self, target):
        self.ClearScreen()
        self.curScreen = target

    def brightnessController(self, information):
        if information.gameState != 0:
            self.lastActiveTime = time.perf_counter()
        if 2 < information.voltage < 3.3 and information.isCharging == False:
            self.lit = not self.lit
            self.lcd.backlight(self.lit)
        elif time.perf_counter() - self.lastActiveTime > self.inactiveTime > 0:
            if self.lit:
                self.lcd.backlight(False)
                self.lit = False
        elif not self.lit:
            self.lcd.backlight(True)
            self.lit = True

    def ClearScreen(self):
        self.lastBatteryIcon = -1
        self.lastChargingState = False
        self.drawn = False
        self.drawnState = -1
        self.lcd.lcd_clear()

    def DrawHome(self, screenInfo, settings):
        if not self.drawn:
            self.ClearScreen()
        self.lcd.lcd_display_string(str(time.localtime()[3]).zfill(2) + ":" + str(time.localtime()[4]).zfill(2), 1)
        if self.charge == "V":
            if screenInfo.voltage < 10:
                volt = f"{screenInfo.voltage:.2f}"
                self.lcd.lcd_display_string_pos(volt, 1, 16 - len(volt) - 3)
        elif self.charge == "%":
            if screenInfo.voltage < 3.3:
                value = "0"
            elif screenInfo.voltage > 4.2:
                value = "100"
            else:
                value = str(round(screenInfo.voltage * 108.88889 - 358.333337)).rjust(4,' ')
            self.lcd.lcd_display_string_pos(value, 1, 16 - len(value) - 3)
        if self.lastChargingState != screenInfo.isCharging:
            if screenInfo.isCharging:
                self.lcd.lcd_display_string_pos('', 1, 15)
                self.lcd.lcd_write_char(7)
            else:
                self.lcd.lcd_display_string_pos(' ', 1, 15)
            self.lastChargingState = screenInfo.isCharging
        icon = CalculateBatteryIcon(screenInfo.voltage)
        if self.lastBatteryIcon != icon:
            self.lcd.lcd_display_string_pos('', 1, 14)
            self.lcd.lcd_write_char(icon)
            self.lastBatteryIcon = icon
        if not self.drawn:
            self.lcd.lcd_display_string_pos(self.charge, 1, 13)
            self.drawn = True
        if self.taken != self.takenDrawn:
            if len(self.taken) == 2:
                text = str(chr(self.taken[0] + 97)) + str(8-self.taken[1])
            else:
                text = '  '
            self.lcd.lcd_display_string_pos(text,1,6)
            self.takenDrawn = self.taken
        if screenInfo.errorState != 0:
            self.lcd.lcd_display_string("                ", 2)
            self.drawError(screenInfo.errorState)
            self.lcd.lcd_display_string("                ", 2)
            self.drawState(screenInfo.gameState, settings)
            self.drawnState = screenInfo.gameState
            screenInfo.errorState = 0
        elif (screenInfo.gameState != self.drawnState or self.toShow != self.lastShown) and screenInfo.gameState != -1:
            chngState = False
            if screenInfo.gameState != self.drawnState:
                chngState = True
            self.drawnState = screenInfo.gameState
            self.lcd.lcd_display_string("                ", 2)
            self.timerActive = False
            self.drawState(screenInfo.gameState, settings, chngState)

    def drawState(self, state, settings, chngState=False):
        if chngState:
            self.hintAvailable = False
        if state == 0:
            self.printState("Idle")
        elif state == 1:
            self.printState("Initializing...")
        elif state == 2:
            self.setTurn(0)
            if not self.timerActive and not self.dontReset:
                self.timerActive = True
                self.startClock(self.whiteTime, settings)
            self.timerActive = True
            self.dontReset = False
        elif state == 3:
            self.setTurn(1)
            if not self.timerActive and not self.dontReset:
                self.timerActive = True
                self.startClock(self.blackTime, settings)
            self.timerActive = True
            self.dontReset = False
        elif state == 5:
            self.printState("Game over!")
            self.setTurn(0)
            self.singleBlink()
            self.gameOver = 0
        elif state == 6:
            self.printState("Game over!")
            self.setTurn(1)
            self.singleBlink()
            self.gameOver = 1
        elif state == 7:
            self.printState("Stalemate!")
            self.setTurn(2)
            self.singleBlink()
            self.gameOver = 2
        elif state == 8:
            self.printState("50 moves!")
            self.setTurn(2)
            self.singleBlink()
            self.gameOver = 2
        elif state == 9:
            self.printState("3 repeats!")
            self.setTurn(2)
            self.singleBlink()
            self.gameOver = 2
        elif state == 4:
            self.setTurn(0)
            self.printState("CHECK!")
            self.singleBlink(0.2,2)
            time.sleep(1)
            self.lcd.lcd_display_string("                ", 2)
            self.setTurn(0)
            if not self.timerActive and not self.dontReset:
                self.timerActive = True
                self.startClock(self.whiteTime, settings)
            self.timerActive = True
            self.dontReset = False
        elif state == 10:
            self.setTurn(1)
            self.printState("CHECK!")
            self.singleBlink(0.2,2)
            time.sleep(1)
            self.lcd.lcd_display_string("                ", 2)
            self.setTurn(1)
            if not self.timerActive and not self.dontReset:
                self.timerActive = True
                self.startClock(self.blackTime, settings)
            self.timerActive = True
            self.dontReset = False
        elif state == 11:
            if self.lastShown != self.toShow:
                self.lastShown = self.toShow
                self.printState(self.toShow)
                self.singleBlink()
        elif state == 12:
            if self.lastShown != self.toShow:
                self.lastShown = self.toShow
                self.printState(self.toShow)
                if self.noBlink:
                    self.noBlink = False
                else:
                    self.singleBlink(sound=2)

    def setTurn(self,color):
        if self.hintAvailable:
            if color == 0:
                self.lcd.lcd_display_string_pos('+',2,0)
                self.curTurn = 0
                self.singleBlink(0.8)
            elif color == 1:
                self.lcd.lcd_display_string_pos('+', 2, 15)
                self.curTurn = 1
                self.singleBlink(0.8)
        else:
            if color == 0:
                self.lcd.lcd_display_string_pos('*',2,0)
                self.curTurn = 0
            elif color == 1:
                self.lcd.lcd_display_string_pos('*', 2, 15)
                self.curTurn = 1
            else:
                self.lcd.lcd_display_string_pos('*', 2, 0)
                self.lcd.lcd_display_string_pos('*', 2, 15)
        pass  # draw a star to show who is playing right now

    def startClock(self, duration, settings):
        self.timerEnd = time.perf_counter() + duration
        self.timerActive = True
        self.runClock(settings)
        pass  # start countdown

    def runClock(self, settings):
        seconds = int(self.timerEnd - time.perf_counter())
        if self.paused or self.hintUsed:
            seconds = self.lastClock
            self.timerEnd = time.perf_counter() + self.lastClock
            self.lcd.lcd_display_string_pos("PAUSE", 2, 5)
        elif self.timerActive:
            if seconds > 0:
                self.lcd.lcd_display_string_pos(str(seconds // 60).zfill(2) + ":" + str(seconds % 60).zfill(2), 2, 5)
                if self.curTurn == 0:
                    overall = settings.whiteTime
                else:
                    overall = settings.blackTime
                if seconds < overall/2 and not self.hintAvailable and self.curHint != '' and settings.assistLevel == 2:
                    self.hintAvailable = True
                    self.setTurn(self.curTurn)
            else:
                self.lcd.lcd_display_string_pos("00:00", 2, 5)
                self.singleBlink()
                if self.punish == " ON":
                    self.lcd.lcd_display_string("                ", 2)
                    self.drawState(self.curTurn*(-1) + 6, settings, chngState=True)
        self.lastClock = seconds
        pass

    def drawError(self, error):
        if error == 1:
            self.printState("Impossible move!")
        elif error == 2:
            self.printState("Wrong color!")
        else:
            self.printState(f"Unknown(id:{error})")
        self.singleBlink(0.2, 2)
        time.sleep(2)
        pass  # 1. implement call for this, print an error by its id, 3. blink once

    def printState(self, string):
        self.lcd.lcd_display_string_pos(string, 2, 8 - math.ceil(len(string)/2))

    def printDialog(self, string, line):
        self.lcd.lcd_display_string_pos(string, line, 8 - math.ceil(len(string) / 2))

    def setPromotion(self):
        self.switchScreen(2)
        self.singleBlink(0.2,2)
        self.toSetPromotion = False

    def singleBlink(self, period=0.5, cycles=1, sound = 1):
        self.toPlay = sound
        for i in range(cycles):
            self.lcd.backlight(False)
            time.sleep(period)
            self.lcd.backlight(True)
            time.sleep(period)
        pass