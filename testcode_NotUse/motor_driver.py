import RPi.GPIO as GPIO
import time
import sys

def main():
    # Set up GPIO mode
    GPIO.setmode(GPIO.BCM)

    # Define the GPIO
    PIN_STEP = 21
    PIN_DIR = 20
    PIN_DIS = 16

    steps_per_revolution = 10_360 
    pulse_half_period = 0.0001

    try:
        # Set up the pin as an output
        GPIO.setup(PIN_STEP, GPIO.OUT)
        GPIO.setup(PIN_DIR, GPIO.OUT)
        GPIO.setup(PIN_DIS, GPIO.OUT)

        # init
        GPIO.output(PIN_STEP, 0)
        GPIO.output(PIN_DIR, 0)
        GPIO.output(PIN_DIS, 0)

        while True:
            for direction in range(2):
                GPIO.output(PIN_DIS, direction)
                GPIO.output(PIN_DIR, direction)
                print(f'direction is {direction}')
                time.sleep(0.1)
                for i in range(steps_per_revolution):
                    for step in range(2):
                        GPIO.output(PIN_STEP, step)
                        time.sleep(pulse_half_period)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Cleaning up...")
    finally:
        # Clean up GPIO settings
        GPIO.cleanup()

if __name__ == "__main__":
        main()
