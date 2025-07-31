import RPi.GPIO as GPIO
import socket
import time

RST = 2 # reset pin for all motors
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbers
GPIO.setup(RST,GPIO.OUT)
GPIO.output(RST, GPIO.HIGH) # Reset motor

# Define pins for 4 motors
DIR_1 = 27 # MOTOR_1
STEP_1 = 17
EN_1 = 15

DIR_2 = 10 # MOTOR_2
STEP_2 = 22
EN_2 = 18

DIR_3 = 11 # MOTOR_3
STEP_3 = 9
EN_3 = 23

DIR_4 = 5 # MOTOR_4
STEP_4 = 0
EN_4 = 24

CW = 1
CCW = 0

# Set up TCP socket to listen for stop signal
HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port number for communication

# PWM configuration
FREQUENCY =  80 # 80Hz suit the encoder 200 ppr resolution
DELAY_ONE_STEP = 1/FREQUENCY
DUTY = 50
class Motor: 
    def __init__(self, DIR:int, STEP:int, EN:int, ID:int)->None:
        """
        Setup GPIO for the motor's direction, step and enable pins
        """
        self.DIR = DIR
        self.STEP = STEP
        self.EN = EN
        self.ID = ID
        
        # GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbers
        GPIO.setup(self.DIR, GPIO.OUT)  # Direction pin
        GPIO.setup(self.STEP, GPIO.OUT)  # Step pin
        GPIO.setup(self.EN, GPIO.OUT)  # Enable pin


    def move_motor(self, direction:int, RUN_STEPS:int)->None:
        """
        Move motor in a given direction with specific steps
        """
        if direction == 1:
            GPIO.output(self.DIR, GPIO.HIGH)
        elif direction == 0:
            GPIO.output(self.DIR, GPIO.LOW)
        GPIO.output(self.EN, GPIO.LOW) # Enable H Bridge  
        # Start PWM and run for request steps
        RUN_TIME = RUN_STEPS * DELAY_ONE_STEP * 2.0
        print(RUN_TIME)
        step = GPIO.PWM(self.STEP,FREQUENCY)
        step.start(DUTY)
        time.sleep(RUN_TIME)
        step.stop()  
        GPIO.output(self.EN, GPIO.HIGH) # Disable H Bridge

    def request_position(self, conn:socket.socket)->float:
        """
        Request capacitor position from encoder
        """
        channel_request = f"{self.ID}"
        conn.sendall(channel_request.encode(encoding='utf-8'))
        message = conn.recv(1024)
        return message.decode(encoding='utf-8')
        # print(f"Motor position: {message.decode(encoding='utf-8')}") # recieve encoder position

    def stop_motor(self):
         """
         Stop the motor.
         """
         print("STOP signal received! Stopping motor...")
         GPIO.output(self.EN, GPIO.HIGH)  # Disable H Bridge
         GPIO.output(self.STEP, GPIO.LOW) # Stop PWM signal

def main():
    """
    Initialize motors.
    """
    GPIO.setwarnings(False)
    motors = [
        Motor(DIR_1, STEP_1, EN_1, 1),
        Motor(DIR_2, STEP_2, EN_2, 2),
        Motor(DIR_3, STEP_3, EN_3, 3),
        Motor(DIR_4, STEP_4, EN_4, 4),
    ]

    try:
    #     # Create a TCP server to receive encoder signals   
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    #         server_socket.bind((HOST, PORT)) # Bind the socket to address and port
    #         server_socket.listen() # Listen for incoming connection
    #         # print(f"Motor control script running, Listening on {HOST}:{PORT}")
    #         while True:
    #             conn, addr = server_socket.accept()
        motors[2].move_motor(CCW, 200)  # Move forward x steps
                # position = motors[1].request_position(conn) # Request position from Encoder.py
                # print(f"Received position from client: {position}")

    except KeyboardInterrupt:
        print("Motor movement stopped by user")
    finally:
        ...
        # time.sleep(5)
        # GPIO.cleanup()
        """
        Calling GPIO.cleanup() will reset the initial pull-up configuration for the ENABLE pin.  
        The PCB design should also allow the RESET pin to be controllable.  
        This is a trade-off solution.
        """

if __name__ == "__main__":
    main()