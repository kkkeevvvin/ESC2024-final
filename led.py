import RPi.GPIO as GPIO
import time

class LED:
    def __init__(self, pin:int=12, freq:int=100) -> None:
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        self.freq = freq
        self.light = GPIO.PWM(pin, freq)
        print("[info] [led] initialized")

    def glow(self, brightness=100, seconds=2) -> None:
        f = self.freq * brightness / 100.0
        if (f > self.freq):
            f = self.freq
        self.light.start(f)
        print("[info] [led] glow: ", f)
        time.sleep(2)

    def stop(self) -> None:
        print("[info] [led] stop")
        self.light.stop()
        pass

if __name__ == "__main__":
    led = LED(32, 100)
    try:
        while True:
            x = int(input("[test] enter a num: "))
            led.glow(x)
    except KeyboardInterrupt:
        del led
        GPIO.cleanup()
