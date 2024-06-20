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

@app.route('/')
def index():
    return render_template(html)

# switch to auto mode
@app.route('/auto')
def led_set_auto():
    led.set_auto_control()
    print("[info] [web] led auto")
    return render_template(html)

@app.route('/user')
def led_set_user():
    led.set_user_control()
    print("[info] [web] led user")
    return render_template(html)

# set led brightness, switch to user mode
@app.route('/setbrightness/<int:brightness>', methods=['POST'])
def led_set_brightness(brightness):
    led.glow(brightness)
    print("[info] [web] led set brightness ", brightness)
    return jsonify({'brightness': led.get_brightness()})

# turn on alarm clock, only work in auto mode
@app.route('/clockon')
def clock_on():
    alarmclock.turnOn()
    return render_template(html)

# turn off alarm clock
@app.route('/clockoff')
def clock_off():
    alarmclock.turnOff()
    return render_template(html)

# set the sleep time, led brightness start to decrease 10 minutes before sleep time
@app.route('/sleep', methods=['POST'])
def set_sleep_time():
    timeval = request.form["time"]
    if timeval == "":
        print("got empty sleep time value")
    else:
        alarmclock.setSleepTime(timeval)
    return render_template(html)

# set wake time, led brightness start to increase, full brightness after 10 minutes
@app.route('/wake', methods=['POST'])
def set_wake_time():
    timeval = request.form["time"]
    if timeval == "":
        print("got empty wake time value")
    else:
        alarmclock.setWakeTime(timeval)
    return render_template(html)

# get states, update web display
@app.route('/illuminance')
def get_illuminance():
    illuminance = lightmeter.get()
    return jsonify({'illuminance': illuminance})

@app.route('/brightness')
def get_brightness():
    return jsonify({'brightness': led.get_brightness()})

@app.route('/usercontrol')
def get_usercontrol():
    state = "auto" if led.get_auto_control() else "user"
    return jsonify({'usercontrol': state})

@app.route('/clockstate')
def get_clock_state():
    state = "on" if alarmclock.getState() else "off"
    return jsonify({'clockstate': state})

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
    curtain.to_state(state)
    return jsonify({'state': curtain.get_state()})

# convert illuminance into led brightness
def auto_bright(illuminance):
    bright = max(min(int(100 * (255 - illuminance) / 255), 100), 0)
    return bright

# led control function for voice control
def lightRegulate(command: str) -> bool:
    global user_control
    #開燈
    if "kaideng" in command:
        try:
            print("[info] [voice control] action: \033[1;32;40mopen the light\033[0m")
            # led.glow(100)
        except:
            print("[warning] [voice control] action: \033[1;31;40mopen light fail\033[0m")

    #關燈
    elif "guandeng" in command:
        try:
            print("[info] [voice control] action: \033[1;31;40mclose the light\033[0m")
            led.glow(0)
        except:
            print("[warning] [voice control] action: \033[1;31;40mclose light fail\033[0m")

    #日光, 自動
    elif "riguang" in command or "zidong" in command:
        try:
            print("[info] [voice control] action: \033[1;33;40mswitch to auto mode\033[0m")
            led.set_auto_control()
        except:
            print("[warning] [voice control] action: \033[1;31;40mswitch mode fail\033[0m")

    #升高
    elif "shengao" in command:
        try:
            print("[info] [voice control] action: \033[1;36;40mincrease brightness\033[0m")
            # led.glow(min(led.get_brightness() + 20, 100))
        except:
            print("[warning] [voice control] action: \033[1;31;40mincrease brightness fail\033[0m")

    #降低
    elif "jiangdi" in command:
        try:
            print("[info] [voice control] action: \033[1;34;40mdecrease brightness\033[0m")
            # led.glow(max(led.get_brightness() - 20, 0))
        except:
            print("[warning] [voice control] action: \033[1;31;40mdecrease brightness fail\033[0m")

    else:
        pass
    return True

# get enviroment light and using auto_bright() to update led brightness every <interval> seconds
def auto_light(interval):
    def update_illumi():
        illumi = lightmeter.get()
        led.set_brightness(auto_bright(illumi))
        print("[info] [auto bright] update: ", illumi, "lux to ", led.get_brightness(), "led brightness")
        led.glow_with_factor(alarmclock.getLightFactor())

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
        led.cleanup()
        GPIO.cleanup()
