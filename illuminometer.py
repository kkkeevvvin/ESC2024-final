#!/usr/bin/python3
#+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|P|i|e|P|i|e|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# camera_preview.py
# Preview from camera
#
# Author : sosorry
# Date   : 04/18/2015
# Usage  : python3 picamera2_cv2_preview.py

import cv2
import time
import numpy as np
from picamera2 import Picamera2

picam2 = Picamera2(0)
# picam2.preview_configuration.main.size = (640, 480)
# picam2.preview_configuration.main.format = "RGB888"
picam2.start()

# Start camera
time.sleep(2)

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("picamera2_cv2", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    average_intensity = np.mean(frame)
    print(f'Average Light Intensity: {average_intensity}')
    time.sleep(1)

# cv2.destroyAllWindows()

