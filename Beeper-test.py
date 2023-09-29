import wiringpi
import time

BuzPin = 26


def setTone(freq):
    if freq != 0:
        wiringpi.pwmSetClock(
            int(
                19.2e6 / 100 / freq
            ))  # set clock divisor (base clock = 19.2 MHz). RealClock = 19.2e6 / clockDivisor/pwmRange
        wiringpi.pwmSetRange(100)  # set range (default = 1024)
        wiringpi.pwmSetMode(0)
        wiringpi.pwmWrite(BuzPin, 50)
    else:
        wiringpi.pwmWrite(BuzPin, 0)


def tone(_, freq, duration):
    setTone(freq)
    time.sleep(duration * 0.001)
    setTone(0)


def delay(ms):
    time.sleep(0.0005 * ms)


def playJedi():
    tone(5, 392, 350);
    delay(350);
    tone(5, 392, 350);
    delay(350);
    tone(5, 392, 350);
    delay(350);
    tone(5, 311, 250);
    delay(250);
    tone(5, 466, 100);
    delay(100);
    tone(5, 392, 350);
    delay(350);
    tone(5, 311, 250);
    delay(250);
    tone(5, 466, 100);
    delay(100);
    tone(5, 392, 700);
    delay(700);

    tone(5, 587, 350);
    delay(350);
    tone(5, 587, 350);
    delay(350);
    tone(5, 587, 350);
    delay(350);
    tone(5, 622, 250);
    delay(250);
    tone(5, 466, 100);
    delay(100);
    tone(5, 369, 350);
    delay(350);
    tone(5, 311, 250);
    delay(250);
    tone(5, 466, 100);
    delay(100);
    tone(5, 392, 700);
    delay(700);

    tone(5, 784, 350);
    delay(350);
    tone(5, 392, 250);
    delay(250);
    tone(5, 392, 100);
    delay(100);
    tone(5, 784, 350);
    delay(350);
    tone(5, 739, 250);
    delay(250);
    tone(5, 698, 100);
    delay(100);
    tone(5, 659, 100);
    delay(100);
    tone(5, 622, 100);
    delay(100);
    tone(5, 659, 450);
    delay(450);

    tone(5, 415, 150);
    delay(150);
    tone(5, 554, 350);
    delay(350);
    tone(5, 523, 250);
    delay(250);
    tone(5, 493, 100);
    delay(100);
    tone(5, 466, 100);
    delay(100);
    tone(5, 440, 100);
    delay(100);
    tone(5, 466, 450);
    delay(450);

    tone(5, 311, 150);
    delay(150);
    tone(5, 369, 350);
    delay(350);
    tone(5, 311, 250);
    delay(250);
    tone(5, 466, 100);
    delay(100);
    tone(5, 392, 750);
    delay(750);


def playDestiny():
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 174, 374.999625);
    delay(416.66625);
    tone(tonePin, 195, 124.999875);
    delay(138.88875);
    tone(tonePin, 220, 499.9995);
    delay(555.555);
    tone(tonePin, 146, 249.99975);
    delay(277.7775);
    tone(tonePin, 146, 249.99975);
    delay(277.7775);
    tone(tonePin, 195, 499.9995);
    delay(555.555);
    tone(tonePin, 174, 374.999625);
    delay(416.66625);
    tone(tonePin, 155, 124.999875);
    delay(138.88875);
    tone(tonePin, 174, 499.9995);
    delay(555.555);
    tone(tonePin, 116, 249.99975);
    delay(277.7775);
    tone(tonePin, 116, 249.99975);
    delay(277.7775);
    tone(tonePin, 130, 499.9995);
    delay(555.555);
    tone(tonePin, 130, 374.999625);
    delay(416.66625);
    tone(tonePin, 146, 124.999875);
    delay(138.88875);
    tone(tonePin, 155, 499.9995);
    delay(555.555);
    tone(tonePin, 155, 374.999625);
    delay(416.66625);
    tone(tonePin, 174, 124.999875);
    delay(138.88875);
    tone(tonePin, 195, 499.9995);
    delay(555.555);
    tone(tonePin, 220, 374.999625);
    delay(416.66625);
    tone(tonePin, 233, 124.999875);
    delay(138.88875);
    tone(tonePin, 261, 749.99925);
    delay(833.3325);
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 293, 499.9995);
    delay(555.555);
    tone(tonePin, 261, 374.999625);
    delay(416.66625);
    tone(tonePin, 233, 124.999875);
    delay(138.88875);
    tone(tonePin, 261, 499.9995);
    delay(555.555);
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 220, 374.999625);
    delay(416.66625);
    tone(tonePin, 195, 124.999875);
    delay(138.88875);
    tone(tonePin, 220, 499.9995);
    delay(555.555);
    tone(tonePin, 146, 374.999625);
    delay(416.66625);
    tone(tonePin, 146, 124.999875);
    delay(138.88875);
    tone(tonePin, 195, 499.9995);
    delay(555.555);
    tone(tonePin, 174, 374.999625);
    delay(416.66625);
    tone(tonePin, 155, 124.999875);
    delay(138.88875);
    tone(tonePin, 174, 499.9995);
    delay(555.555);
    tone(tonePin, 116, 374.999625);
    delay(416.66625);
    tone(tonePin, 116, 124.999875);
    delay(138.88875);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 220, 374.999625);
    delay(416.66625);
    tone(tonePin, 195, 124.999875);
    delay(138.88875);
    tone(tonePin, 174, 999.999);
    delay(1111.11);
    tone(tonePin, 293, 999.999);
    delay(1111.11);
    tone(tonePin, 261, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 249.99975);
    delay(277.7775);
    tone(tonePin, 220, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 249.99975);
    delay(277.7775);
    tone(tonePin, 261, 749.99925);
    delay(833.3325);
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 174, 999.999);
    delay(1111.11);
    tone(tonePin, 233, 999.999);
    delay(1111.11);
    tone(tonePin, 220, 249.99975);
    delay(277.7775);
    tone(tonePin, 195, 249.99975);
    delay(277.7775);
    tone(tonePin, 174, 249.99975);
    delay(277.7775);
    tone(tonePin, 195, 249.99975);
    delay(277.7775);
    tone(tonePin, 220, 749.99925);
    delay(833.3325);
    tone(tonePin, 146, 249.99975);
    delay(277.7775);
    tone(tonePin, 146, 999.999);
    delay(1111.11);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 195, 374.999625);
    delay(416.66625);
    tone(tonePin, 220, 124.999875);
    delay(138.88875);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 195, 374.999625);
    delay(416.66625);
    tone(tonePin, 220, 124.999875);
    delay(138.88875);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 195, 374.999625);
    delay(416.66625);
    tone(tonePin, 233, 124.999875);
    delay(138.88875);
    tone(tonePin, 311, 999.999);
    delay(1111.11);
    tone(tonePin, 311, 999.999);
    delay(1111.11);
    tone(tonePin, 293, 249.99975);
    delay(277.7775);
    tone(tonePin, 261, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 249.99975);
    delay(277.7775);
    tone(tonePin, 261, 249.99975);
    delay(277.7775);
    tone(tonePin, 293, 749.99925);
    delay(833.3325);
    tone(tonePin, 233, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 999.999);
    delay(1111.11);
    tone(tonePin, 261, 999.999);
    delay(1111.11);
    tone(tonePin, 233, 249.99975);
    delay(277.7775);
    tone(tonePin, 220, 249.99975);
    delay(277.7775);
    tone(tonePin, 195, 249.99975);
    delay(277.7775);
    tone(tonePin, 220, 249.99975);
    delay(277.7775);
    tone(tonePin, 233, 749.99925);
    delay(833.3325);
    tone(tonePin, 195, 249.99975);
    delay(277.7775);
    tone(tonePin, 195, 999.999);
    delay(1111.11);
    tone(tonePin, 233, 499.9995);
    delay(555.555);
    tone(tonePin, 220, 374.999625);
    delay(416.66625);
    tone(tonePin, 195, 124.999875);
    delay(138.88875);
    tone(tonePin, 174, 499.9995);
    delay(555.555);
    tone(tonePin, 116, 374.999625);
    delay(416.66625);
    tone(tonePin, 116, 124.999875);
    delay(138.88875);
    tone(tonePin, 174, 999.999);
    delay(1111.11);
    tone(tonePin, 195, 499.9995);
    delay(555.555);
    tone(tonePin, 220, 499.9995);
    delay(555.555);
    tone(tonePin, 233, 1999.998);
    delay(2222.22);


tonePin= BuzPin
wiringpi.wiringPiSetup()
wiringpi.pinMode(BuzPin, 2)  # set servo pin to PWM mode (0=input,1=output,2=pwm output)
setTone(0)
while True:
    #playJedi()
    #playDestiny()
    time.sleep(1)
