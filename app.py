from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
import threading
import time

from illuminometer import Illuminometer
from stepmotor import StepperMotor
from led import LED
from STT import VoiceControl
from alarmclock import AlarmClock

app = Flask(__name__)
led = LED(32)
lightmeter = Illuminometer()
curtain = StepperMotor()
alarmclock = AlarmClock(8)
html = "index.html"

curtain_lock = threading.Lock()
led_lock = threading.Lock()

brightness = 0
user_control = False

@app.route('/')
def index():
    return render_template(html)

# open the light, switch to user mode
@app.route('/on')
def led_on():
    global user_control
    global brightness
    with led_lock:
        brightness = 100
        led.glow(brightness)
        user_control = True
    print("led on")
    return render_template(html)

# close the light, switch to user mode
@app.route('/off')
def led_off():
    global user_control
    global brightness
    with led_lock:
        brightness = 0
        led.glow(brightness)
        user_control = True
    print("led off")
    return render_template(html)

# switch to auto mode
@app.route('/auto')
def led_auto():
    global user_control
    global brightness
    with led_lock:
        user_control = False
        brightness = auto_bright(lightmeter.get())
        led.glow(int(brightness * alarmclock.getLightFactor()))
    print("led off")
    return render_template(html)

"""
@app.route('/up')
def led_incr_bright():
    global user_control
    global brightness
    with led_lock:
        brightness = min(brightness+20, 100)
        led.glow(brightness)
        user_control = True
    print("led increase brightness")
    return render_template(html)

@app.route('/down')
def led_decr_bright():
    global user_control
    global brightness
    with led_lock:
        brightness = max(brightness-20, 0)
        led.glow(brightness)
        user_control = True
    print("led decrease brightness")
    return render_template(html)
"""

# set led brightness, switch to user mode
@app.route('/setbrightness/<int:value>', methods=['POST'])
def led_set_bright(value):
    global user_control
    global brightness
    with led_lock:
        try:
            brightness = int(value)
            led.glow(brightness)
            user_control = True
            print("led set brightness ", value)
        except:
            pass
    return jsonify({'brightness': brightness})

# turn on alarm clock, only work in auto mode
@app.route('/clockon')
def clock_on():
    global brightness
    global user_control
    with led_lock:
        alarmclock.turnOn()
        if (not user_control):
            led.glow(int(brightness * alarmclock.getLightFactor()))
    return render_template(html)

# turn off alarm clock
@app.route('/clockoff')
def clock_off():
    global brightness
    global user_control
    with led_lock:
        alarmclock.turnOff()
        if (not user_control):
            led.glow(brightness)
    return render_template(html)

# set the sleep time, led brightness start to decrease 10 minutes before sleep time
@app.route('/sleep', methods=['POST'])
def set_sleep_time():
    global brightness
    global user_control
    timeval = request.form["time"]
    if timeval == "":
        print("got empty sleep time value")
    else:
        with led_lock:
            alarmclock.setSleepTime(timeval)
            if (not user_control):
                led.glow(int(brightness * alarmclock.getLightFactor()))
        #print("set sleep time", timeval)
    return render_template(html)

# set wake time, led brightness start to increase, full brightness after 10 minutes
@app.route('/wake', methods=['POST'])
def set_wake_time():
    global brightness
    global user_control
    timeval = request.form["time"]
    if timeval == "":
        print("got empty wake time value")
    else:
        with led_lock:
            alarmclock.setWakeTime(timeval)
            if (not user_control):
                led.glow(int(brightness * alarmclock.getLightFactor()))
        #print("set wake time", timeval)
    return render_template(html)

# get states, update web display
@app.route('/illuminance')
def get_illuminance():
    illuminance = lightmeter.get()
    return jsonify({'illuminance': illuminance})

@app.route('/brightness')
def get_brightness():
    global brightness
    return jsonify({'brightness': brightness})

@app.route('/usercontrol')
def get_usercontrol():
    global user_control
    if user_control:
        return jsonify({'usercontrol': "user"})
    else:
        return jsonify({'usercontrol': "auto"})

@app.route('/clockstate')
def get_clock_state():
    if (alarmclock.getState()):
        return jsonify({'clockstate': "on"})
    else:
        return jsonify({'clockstate': "off"})

@app.route('/sleeptime')
def get_sleep_time():
    timeval = alarmclock.getSleepTime()
    return jsonify({'sleeptime': timeval})

@app.route('/waketime')
def get_wake_time():
    timeval = alarmclock.getWakeTime()
    return jsonify({'waketime': timeval})

# curtain control
@app.route('/curtain/<int:state>', methods=['POST'])
def set_curtain_state(state):
    with curtain_lock:
        curtain.to_state(state)
    return jsonify({'state': curtain.get_state()})

class PID:
    def __init__(self, P=1.0, I=0.0, D=0.0):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time

        self.clear()

    def clear(self):
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        self.int_error = 0.0
        self.windup_guard = 20.0
        self.output = 0.0

    def update(self, feedback_value):
        error = self.SetPoint - feedback_value

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if delta_time >= self.sample_time:
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if self.ITerm < -self.windup_guard:
                self.ITerm = -self.windup_guard
            elif self.ITerm > self.windup_guard:
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    def setKp(self, proportional_gain):
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        self.Kd = derivative_gain

    def setWindup(self, windup):
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time

pid = PID(P=0.005, I=0.035, D=0.001)  # Adjust PID constants as needed
pid.SetPoint = 150 # Target illuminance

def auto_bright(illuminance):
    pid.update(illuminance)
    brightness = max(min(int(100 * pid.output), 100), 0)
    return brightness

# led control function for voice control
def lightRegulate(command:str) -> bool:
    global user_control
    global brightness
    #開燈
    if "kaideng" in command:
        try:
            print("[info] [voice control] action: \033[1;32;40mopen the light\033[0m")
            with led_lock:
                brightness = 100
                led.glow(brightness)
                user_control = True
        except:
            print("[warning] [voice control] action: \033[1;31;40mopen light fail\033[0m")

    #關燈
    elif "guandeng" in command:
        try:
            print("[info] [voice control] action: \033[1;31;40mclose the light\033[0m")
            with led_lock:
                brightness = 0
                led.glow(brightness)
                user_control = True
        except:
            print("[warning] [voice control] action: \033[1;31;40mclose light fail\033[0m")

    #日光, 自動
    elif "riguang" in command or "zidong" in command:
        try:
            print("[info] [voice control] action: \033[1;33;40mswitch to auto mode\033[0m")
            with led_lock:
                user_control = False
                brightness = auto_bright(lightmeter.get())
                led.glow(int(brightness * alarmclock.getLightFactor()))
        except:
            print("[warning] [voice control] action: \033[1;31;40mswitch mode fail\033[0m")

    #升高
    elif "shengao" in command:
        try:
            print("[info] [voice control] action: \033[1;36;40mincrease brightness\033[0m")
            with led_lock:
                user_control = True
                brightness = min(brightness+20, 100)
                led.glow(brightness)
        except:
            print("[warning] [voice control] action: \033[1;31;40mincrease brightness fail\033[0m")

    #降低
    elif "jiangdi" in command:
        try:
            print("[info] [voice control] action: \033[1;34;40mdecrease brightness\033[0m")
            with led_lock:
                user_control = True
                brightness = max(brightness-20, 0)
                led.glow(brightness)
        except:
            print("[warning] [voice control] action: \033[1;31;40mdecrease brightness fail\033[0m")

    #離開, stop voice control
    #elif "likai" in command:
    #    print("\033[1;35;40mPi: stop\033[0m")
    #    return False
    else:
        pass
    return True

# get enviroment light and using auto_bright() to update led brightness every <interval> seconds
def auto_light(interval):
    global brightness
    global led
    global user_control

    def update_illumi():
        global brightness
        global user_control
        with led_lock:
            if (not user_control):
                illumi = lightmeter.get()
                brightness = auto_bright(illumi)
                print("[info] [auto bright] update: ", illumi, "lux to ", brightness, "led brightness")
                led.glow(int(brightness * alarmclock.getLightFactor()))

    def set_interval(interval):
        try:
            while True:
                update_illumi()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("[info] [auto bright] stop")

    timer = threading.Thread(target=set_interval, args=(interval,))
    timer.start()
    

if __name__ == '__main__':
    try:
        auto_light(5)
        vc = VoiceControl(lightRegulate, "vosk-model-small-cn-0.22")
        vc.startThread()
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
