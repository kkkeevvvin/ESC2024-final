#!/usr/bin/python3

import cv2
import time
import numpy as np
from picamera2 import Picamera2

class Illuminometer:
    def __init__(self):
        self.camera = Picamera2(0)
        self.camera.set_controls({"ExposureTime": 1000})
        self.camera.set_controls({"AwbEnable": False})
        self.camera.set_controls({"AnalogueGain": 1.0})
        self.camera.start()

    def get(self):
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_intensity = np.mean(frame)
        return average_intensity


if __name__ == "__main__":
    x = Illuminometer()
    print(x.get())
