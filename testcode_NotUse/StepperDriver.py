from time import sleep
import RPi.GPIO as GPIO

DIR = 10
STEP = 22
EN = 18
CW = 1
CCW = 0
SPR = 480

GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)
GPIO.output(DIR, CW)
GPIO.output(EN, GPIO.HIGH) # Enable pin for H Bridge - Active Low

step_count = SPR
delay = .010

GPIO.output(EN, GPIO.LOW) # Enable H Bridge

for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    print("Toggle \n %d" % (x))
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)
        
GPIO.output(EN, GPIO.HIGH) # Disable H Bridge

print("Delay = %f " % (delay))
