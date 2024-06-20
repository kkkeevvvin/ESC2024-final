import RPi.GPIO as GPIO
import threading

class LED:
    def __init__(self, pin: int = 12, freq: int = 100) -> None:
        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)

        self.pwm = GPIO.PWM(pin, freq)
        self.pwm.start(0)
        self.brightness = 0

        self.lock = threading.Lock()
        self.auto_control = False

        print("[info] [led] initialized")

    def set_brightness(self, brightness):
        if self.get_user_control():
            if 0 <= brightness <= 100:
                self.brightness = brightness
            else:
                print("[error] [led] brightness should be in 0 ~ 100")
        else:
            print("[error] [led] set brightness is auto mode")

    def get_brightness(self) -> int:
        return self.brightness

    def set_auto_control(self):
        self.auto_control = True

    def set_user_control(self):
        self.auto_control = False

    def get_auto_control(self):
        return self.auto_control
    
    def get_user_control(self):
        return not self.auto_control

    def glow(self, brightness=100) -> None:
        if self.get_user_control():
            with self.lock:
                self.set_brightness(brightness)
                self.pwm.ChangeDutyCycle(brightness)
                print("[info] [led] glow: ", brightness)
        else:
            print("[error] [led] set brightness in auto mode")

    def glow_with_factor(self, factor):
        if self.get_auto_control():
            with self.lock:
                factored_brightness = self.get_brightness() * factor
                self.pwm.ChangeDutyCycle(factored_brightness)
                print("[info] [led] glow with factor: ", factor)
        else:
            print("[error] [led] set factor in user mode")

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
