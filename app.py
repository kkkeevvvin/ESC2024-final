from flask import Flask, render_template_string
import RPi.GPIO as GPIO

app = Flask(__name__)
lightmeter = Illminometer()

# HTML template
html = """
<!DOCTYPE html>
<html>
<head>
    <title>LED Control and Light Meter</title>
    <script>
        function getIlluminance() {
            fetch('/illuminance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('illuminance').innerText = data.illuminance;
                });
        }
        setInterval(getIlluminance, 1000);
        window.onload = getIlluminance;
    </script>
</head>
<body>
    <h1>Control LED</h1>
    <form action="/on">
        <button type="submit">Turn ON</button>
    </form>
    <form action="/off">
        <button type="submit">Turn OFF</button>
    </form>
    <h2>Current Illuminance: <span id="illuminance">Loading...</span> lux</h2>
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

@app.route('/illuminance')
def get_illuminance():
    illuminance = lightmeter.get()
    return jsonify({'illuminance': illuminance})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
