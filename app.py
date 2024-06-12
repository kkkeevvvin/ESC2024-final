from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import threading

from illuminometer import Illuminometer
from stepmotor import StepperMotor

app = Flask(__name__)
lightmeter = Illuminometer()
curtain = StepperMotor()
html = "index.html"

curtain_lock = threading.Lock()

@app.route('/')
def index():
    return render_template(html)

@app.route('/on')
def led_on():
    # GPIO.output(LED_PIN, GPIO.HIGH)
    print("led on")
    return render_template(html)

@app.route('/off')
def led_off():
    # GPIO.output(LED_PIN, GPIO.LOW)
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

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
