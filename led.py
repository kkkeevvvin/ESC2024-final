import RPi.GPIO as GPIO

class LED:
    def __init__(self, pin: int = 12, freq: int = 100) -> None:
        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)

        self.pwm = GPIO.PWM(pin, freq)
        self.pwm.start(0)
        self.brightness = 0
        print("[info] [led] initialized")

    def glow(self, brightness=100) -> None:
        self.set_brightness(brightness)
        self.pwm.ChangeDutyCycle(brightness)
        print("[info] [led] glow: ", brightness)

    def set_brightness(self, brightness):
        if 0 <= brightness <= 100:
            self.brightness = brightness
        else:
            print("[error] [led] brightness should be in 0 ~ 100")

    def get_brightness(self) -> int:
        return self.brightness

    def cleanup(self) -> None:
        print("[info] [led] stop")
        self.pwm.stop()

if __name__ == "__main__":
    led = LED(32)
    try:
        while True:
            x = int(input("[test] enter a num: "))
            led.glow(x)
    except KeyboardInterrupt:
        led.cleanup()
        GPIO.cleanup()
