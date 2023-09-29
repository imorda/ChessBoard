import os
import random

NEXTTURN = 0
GAMEOVER = 1
GAMESTART = 2
SCREENERROR = 3
LEDERROR = 4
SCREENNOTIFY = 5
enabled = " ON"


def playFile(file):
    if enabled == " ON":
        os.system("omxplayer -o local --no-keys " + file + " &")


def playDir(dir):
    try:
        onlyfiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
        playFile(dir+"/"+onlyfiles[random.randint(0,len(onlyfiles)-1)])
    except:
        print("No sound file!")


def playEvent(event):
    if event == NEXTTURN:
        playDir("sounds/next_turn")
    if event == GAMEOVER:
        playDir("sounds/game_over")
    if event == GAMESTART:
        playDir("sounds/game_start")
    if event == SCREENERROR:
        playDir("sounds/screen_error")
    if event == LEDERROR:
        playDir("sounds/led_error")
    if event == SCREENNOTIFY:
        playDir("sounds/screen_notify")
