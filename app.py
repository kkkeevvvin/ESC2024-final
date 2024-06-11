from flask import Flask, render_template_string
import RPi.GPIO as GPIO

# Setup
# GPIO.setmode(GPIO.BCM)
# LED_PIN = 17
# GPIO.setup(LED_PIN, GPIO.OUT)

app = Flask(__name__)

# HTML template
html = """
<!DOCTYPE html>
<html>
<head>
    <title>LED Control</title>
</head>
<body>
    <h1>Control LED</h1>
    <form action="/on">
        <button type="submit">Turn ON</button>
    </form>
    <form action="/off">
        <button type="submit">Turn OFF</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/on')
def led_on():
    # GPIO.output(LED_PIN, GPIO.HIGH)
    print("led on")
    return render_template_string(html)

@app.route('/off')
def led_off():
    # GPIO.output(LED_PIN, GPIO.LOW)
    print("led off")
    return render_template_string(html)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
