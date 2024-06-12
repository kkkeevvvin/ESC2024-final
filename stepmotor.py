import RPi.GPIO as GPIO
import time

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

    def setStep(self, step):
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def check_avail_state_rotations(self, state):
        # return True if available
        if state >= self.state_rotations_min and state <= self.state_rotations_max:
            return True
        else:
            return False

    def forward(self, delay, rotations):
        # print("forward")
        for _ in range(rotations):
            # if not self.check_avail_state_rotations(self.state_rotations + 1):
            #     break
            for step in self.Seq:
                self.setStep(step)
                time.sleep(delay)
            self.state_rotations += 1
        print(f"cur state rot: {self.state_rotations}")
            
    def backward(self, delay, rotations):
        # print("backward")
        for _ in range(rotations):
            # if not self.check_avail_state_rotations(self.state_rotations - 1):
            #     break
            for step in reversed(self.Seq):
                self.setStep(step)
                time.sleep(delay)
            self.state_rotations -= 1
        print(f"cur state rot: {self.state_rotations}")

    def to_state_rotations(self, state_rotations_next):
        if state_rotations_next < self.state_rotations_min or \
                state_rotations_next > self.state_rotations_max:
            print(f"state_rotation should be in range {self.state_rotations_min} ~ {self.state_rotations_max}.")
            return

        if   state_rotations_next < self.state_rotations:
            self.backward(0.001, self.state_rotations - state_rotations_next)
        elif state_rotations_next > self.state_rotations:
            self.forward(0.001, state_rotations_next - self.state_rotations)

    def to_state(self, state_next):
        if state_next < self.state_min or state_next > self.state_max:
            print(f"state range should be in range {self.state_min} ~ {self.state_max}.")
            return
        
        state_rotations_next = state_next * int(self.state_rotations_max / self.state_max)

        self.to_state_rotations(state_rotations_next)
        self.state = state_next

    def get_state(self):
        return self.state
    
    def cleanup(self):
        GPIO.cleanup()

if __name__ == '__main__':
    motor_pins = [11, 12, 13, 15]  # Example pin numbers for GPIO.BOARD
    motor = StepperMotor(motor_pins)
    try:
        while True:
            state = int(input("enter num of the forward rotations: "))
            # motor.to_state(state)
            motor.forward(0.001, state)
            state = int(input("enter num of the backward rotations: "))
            motor.backward(0.001, state)
    except KeyboardInterrupt:
        pass
    finally:
        motor.cleanup()

