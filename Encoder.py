import RPi.GPIO as GPIO
import socket
from time import sleep
import pickle
import os

ENCODER_SAVE_FILE = "encoders.pkl"  # File to save encoder positions

# Define GPIO pins for encoder channels
ENCODER_A_1 = 6  # GPIO pin for Channel A_1
ENCODER_B_1 = 13  # GPIO pin for Channel B_1
INDEX_1 = 17  # GPIO pin for Index Channel X_1

ENCODER_A_2 = 25  # GPIO pin for Channel A_2
ENCODER_B_2 = 8  # GPIO pin for Channel B_2
INDEX_2 = 7  # GPIO pin for Index Channel X_2

ENCODER_A_3 = 1  # GPIO pin for Channel A_3
ENCODER_B_3 = 12  # GPIO pin for Channel B_3
INDEX_3 = 16  # GPIO pin for Index Channel X_3

ENCODER_A_4 = 20  # GPIO pin for Channel A_4
ENCODER_B_4 = 21  # GPIO pin for Channel B_4
INDEX_4 = 26  # GPIO pin for Index Channel X_4


# Set up TCP socket
HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port number for communication

# Initialize global variables !! load the initialize position   
position = 0
last_a_state = None

class channel_command:
    CALIBRATE = 0
    REQ_POS_MOTOR_1 = 1
    REQ_POS_MOTOR_2 = 2
    REQ_POS_MOTOR_3 = 3
    REQ_POS_MOTOR_4 = 4

class Encoder:
    def __init__(self, ENCODER_A:int, ENCODER_B:int, INDEX:int, ID:int)->None:
        """
        Setup GPIO for the encoder A, B, X pins
        """
        self.ENCODER_A = ENCODER_A
        self.ENCODER_B = ENCODER_B
        self.INDEX = INDEX
        self.ID = ID
        self.position = position
        
    def initGPIO(self):
        """
        Initialize GPIO and add event
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ENCODER_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.ENCODER_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.INDEX, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.ENCODER_A, GPIO.BOTH, callback=self.encoder_callback)
 

    def encoder_callback(self, channel)->None:
        """
        Callback function for Channel A
        """
        if GPIO.input(self.ENCODER_A) == GPIO.input(self.ENCODER_B):
            self.position += 1
        else:
            self.position -= 1

def calibrate(encoders)->None:
    for encoder in encoders:
        encoder.position = 0
    with open(ENCODER_SAVE_FILE,'wb') as file:
        pickle.dump(encoders,file)

def main():
    # if file does not exist
    if os.path.exists(ENCODER_SAVE_FILE):
        with open(ENCODER_SAVE_FILE,'rb') as file:
            encoders = pickle.load(file)
    else:
        encoders = [
            Encoder(ENCODER_A_1, ENCODER_B_1, INDEX_1, 1),
            Encoder(ENCODER_A_2, ENCODER_B_2, INDEX_2, 2),
            Encoder(ENCODER_A_3, ENCODER_B_3, INDEX_3, 3),
            Encoder(ENCODER_A_4, ENCODER_B_4, INDEX_4, 4)
        ]
    
    for encoder in encoders:
        encoder.initGPIO()
        # print(f"{encoder.position}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            # print(f"Connected to server at {HOST}:{PORT}")
            while True:
                conn, addr = server_socket.accept()
                # Receive the server's message (channel request)
                message = conn.recv(1024)
                channel = message.decode(encoding='utf-8').strip()
                print(f"Server requested: {channel}")
                if int(channel) == channel_command.CALIBRATE: # if the reset command is recieved
                    calibrate(encoders)
                    for encoder in encoders:
                        print(f"{encoder.position}")
                else:
                    # Find the position for the requested channel
                    for encoder in encoders:
                        if encoder.ID == int(channel):
                            print(f"{encoder.position}")
                            conn.sendall(f"{encoder.position}".encode(encoding='utf-8'))
                            # saves encoder positions to a file using pickle
                            with open(ENCODER_SAVE_FILE,'wb') as file:
                                pickle.dump(encoders,file)
                            # exit for loop
                            break
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()