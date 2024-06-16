from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import threading
import time

from illuminometer import Illuminometer
from stepmotor import StepperMotor
from led import LED
from STT import VoiceControl

app = Flask(__name__)
led = LED(32)
lightmeter = Illuminometer()
curtain = StepperMotor()
html = "index.html"

curtain_lock = threading.Lock()
led_lock = threading.Lock()

brightness = 0
user_control = False

@app.route('/')
def index():
    return render_template(html)

@app.route('/on')
def led_on():
    global user_control
    with led_lock:
        led.glow(100)
        user_control = True
    print("led on")
    return render_template(html)

@app.route('/off')
def led_off():
    global user_control
    with led_lock:
        led.glow(0)
        user_control = True
    print("led off")
    return render_template(html)

@app.route('/illuminance')
def get_illuminance():
    illuminance = lightmeter.get()
    return jsonify({'illuminance': illuminance})

@app.route('/curtain/<int:state>', methods=['POST'])
def set_curtain_state(state):
    with curtain_lock:
        curtain.to_state(state)
    return jsonify({'state': curtain.get_state()})


def illumi_to_bright(illuminance):
    bright = max(min(int(100*(255 - illuminance)/255), 100), 0)
    return bright

def lightRegulate(command:str) -> bool:
    global user_control
    global brightness
    #開燈
    if "kaideng" in command:
        try:
            print("[info] [voice control] action: \033[1;32;40mopen the light\033[0m")
            with led_lock:
                led.glow(100)
                user_control = True
        except:
            print("[warning] [voice control] action: \033[1;31;40mopen light fail\033[0m")

    #關燈
    elif "guandeng" in command:
        try:
            print("[info] [voice control] action: \033[1;31;40mclose the light\033[0m")
            with led_lock:
                led.glow(0)
                user_control = True
        except:
            print("[warning] [voice control] action: \033[1;31;40mclose light fail\033[0m")

    #日光, 自動
    elif "riguang" in command or "zidong" in command:
        try:
            print("[info] [voice control] action: \033[1;33;40mswitch to auto mode\033[0m")
            with led_lock:
                user_control = False
                brightness = illumi_to_bright(lightmeter.get())
                led.glow(brightness)
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
                brightness = illumi_to_bright(illumi)
                print("[info] [auto bright] update: ", illumi, "lux to ", brightness, "led brightness")
                led.glow(brightness)

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
