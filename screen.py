import I2C_LCD_driver
import time
import math


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
    drawn = False
    gameOver = -1
    lastBatteryIcon = -1
    lastChargingState = False
    curTurn = 0
    lit = True
    timerEnd = 0
    timerActive = False
    drawnState = -1
    whiteTime = 120
    takenDrawn = tuple()
    taken = tuple()
    blackTime = 6
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

    lcd.lcd_load_custom_chars(customChars)

    def __init__(self, inactiveTime = 60, whiteTime=120, blackTime=6):
        self.whiteTime = whiteTime
        self.blackTime = blackTime
        self.inactiveTime = inactiveTime
        self.drawn = False
        self.lcd.backlight(True)
        self.lit = True

    def RunThread(self, screenInfo, taken):
        self.taken = taken
        self.brightnessController(screenInfo)
        if self.curScreen == 0:
            self.DrawHome(screenInfo)
            self.runClock()

    def brightnessController(self, information):
        if 2 < information.voltage < 3.3 and information.isCharging == False:
            self.lit = not self.lit
            self.lcd.backlight(self.lit)
        elif time.perf_counter() - self.lastActiveTime > self.inactiveTime:
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
        self.lcd.lcd_clear()

    def DrawHome(self, screenInfo):
        if not self.drawn:
            self.ClearScreen()
        self.lcd.lcd_display_string(str(time.localtime()[3]).zfill(2) + ":" + str(time.localtime()[4]).zfill(2), 1)
        volt = f"{screenInfo.voltage:.2f}"
        self.lcd.lcd_display_string_pos(volt, 1, 16 - len(volt) - 2)
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
            self.lcd.lcd_display_string_pos("V", 1, 16 - len(volt) - 3)
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
            self.drawState(screenInfo.gameState)
            self.drawnState = screenInfo.gameState
            screenInfo.errorState = 0
        elif screenInfo.gameState != self.drawnState and screenInfo.gameState != -1:
            self.lcd.lcd_display_string("                ", 2)
            self.timerActive = False
            self.drawState(screenInfo.gameState)
            self.drawnState = screenInfo.gameState

    def drawState(self, state):
        if state == 0:
            self.printState("Idle")
        elif state == 1:
            self.printState("Initializing...")
        elif state == 2:
            self.setTurn(0)
            if not self.timerActive:
                self.timerActive = True
                self.startClock(self.whiteTime)
        elif state == 3:
            self.setTurn(1)
            if not self.timerActive:
                self.timerActive = True
                self.startClock(self.blackTime)
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
            if not self.timerActive:
                self.timerActive = True
                self.startClock(self.whiteTime)
        elif state == 10:
            self.setTurn(1)
            self.printState("CHECK!")
            self.singleBlink(0.2,2)
            time.sleep(1)
            self.lcd.lcd_display_string("                ", 2)
            self.setTurn(1)
            if not self.timerActive:
                self.timerActive = True
                self.startClock(self.blackTime)

    def setTurn(self,color):
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

    def startClock(self, duration):
        self.timerEnd = time.perf_counter() + duration
        self.timerActive = True
        self.runClock()
        pass  # start countdown

    def runClock(self):
        seconds = int(self.timerEnd - time.perf_counter())
        if self.timerActive:
            if seconds > 0:
                self.lcd.lcd_display_string_pos(str(seconds // 60).zfill(2) + ":" + str(seconds % 60).zfill(2), 2, 5)
            else:
                self.lcd.lcd_display_string_pos("00:00", 2, 5)
                self.singleBlink()
                self.lcd.lcd_display_string("                ", 2)
                self.drawState(self.curTurn*(-1) + 6)

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

    def setPromotion(self):
        self.ClearScreen()
        self.lcd.lcd_display_string(" Queen  Bishop~", 1)
        self.lcd.lcd_display_string("X Knight Rook OK", 2)
        self.singleBlink(0.2,2)
        return 1  # call clear screen 2. draw menu for this 3. blink once

    def singleBlink(self, period=0.5, cycles=1):
        for i in range(cycles):
            self.lcd.backlight(False)
            time.sleep(period)
            self.lcd.backlight(True)
            time.sleep(period)
        pass