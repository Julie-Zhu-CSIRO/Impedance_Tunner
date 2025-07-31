import time
import RPi.GPIO as GPIO

DIR = 27
STEP = 17
EN = 15

CW = 1
CCW = 0
SPR = 480
FREQUENCY = 100 #100Hz

GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)
GPIO.output(DIR, CCW)
GPIO.output(EN, GPIO.HIGH) # Enable pin for H Bridge - Active Low


GPIO.output(EN, GPIO.LOW) # Enable H Bridge

step = GPIO.PWM(STEP,FREQUENCY) #set frequency to 10kHz
step.start(50) #start PWM with 50% duty cycle
    
time.sleep(10)
step.stop()        
GPIO.output(EN, GPIO.HIGH) # Disable H Bridge

print("Delay = %f " % (delay))
