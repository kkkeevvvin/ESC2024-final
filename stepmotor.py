import RPi.GPIO as GPIO
import time

S_ = "[stepmotor] "
S_info = "[info] " + S_
S_error = "[error] " + S_
S_test = "[test] " + S_

class StepperMotor:
    def __init__(self, pins = [11,12,13,15]):
        self.pins = pins
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
        
        self.StepCount = 8
        self.Seq = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
        ]

        self.state = 0
        self.state_min = 0
        self.state_max = 10

        self.state_rotations = 0
        self.state_rotations_min = 0
        self.state_rotations_max = 3200

        print(S_info + "initialized")

    def setStep(self, step):
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def forward(self, delay, rotations):
        for _ in range(rotations):
            for step in self.Seq:
                self.setStep(step)
                time.sleep(delay)
            self.state_rotations += 1
        print(S_info + f"cur state rot: {self.state_rotations}")
            
    def backward(self, delay, rotations):
        for _ in range(rotations):
            for step in reversed(self.Seq):
                self.setStep(step)
                time.sleep(delay)
            self.state_rotations -= 1
        print(S_info + f"cur state rot: {self.state_rotations}")

    def to_state_rotations(self, state_rotations_next):
        if state_rotations_next < self.state_rotations_min or \
                state_rotations_next > self.state_rotations_max:
            print(S_error + f"state_rotation should be in range {self.state_rotations_min} ~ {self.state_rotations_max}.")
            return

        if   state_rotations_next < self.state_rotations:
            self.backward(0.001, self.state_rotations - state_rotations_next)
        elif state_rotations_next > self.state_rotations:
            self.forward(0.001, state_rotations_next - self.state_rotations)

    def to_state(self, state_next):
        if state_next < self.state_min or state_next > self.state_max:
            print(S_info + f"state range should be in range {self.state_min} ~ {self.state_max}.")
            return
        
        state_rotations_next = state_next * int(self.state_rotations_max / self.state_max)

        self.to_state_rotations(state_rotations_next)
        self.state = state_next

    def get_state(self):
        return self.state
    
    def cleanup(self):
        GPIO.cleanup()

if __name__ == '__main__':
    motor_pins = [11, 12, 13, 15]
    motor = StepperMotor(motor_pins)
    try:
        while True:
            state = int(input(S_test + "enter num of the forward rotations: "))
            motor.forward(0.001, state)
            state = int(input(S_test + "enter num of the backward rotations: "))
            motor.backward(0.001, state)
    except KeyboardInterrupt:
        pass
    finally:
        motor.cleanup()

