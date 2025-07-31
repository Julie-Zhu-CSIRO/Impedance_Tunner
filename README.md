# Motor Control & VNA Web Interface
This project provides a Python Flask web application that integrates two key components:
- A Motor Driver module
- VNA (Vector Network Analyzer) control
The components communicate via a local TCP socket to enable coordinated motor control and VNA data acquisition.

## Features
- **Motor Control**: Control up to four motors, move them by specified steps, and calibrate their positions.

- **VNA Impedance Measurement**: Get real and imaginary impedance values from a VNA at a specified frequency.

- **GUI**:
    - Enhanced Impedance History: Each impedance measurement now logs comprehensive data

    - Smith Chart Visualization: All measured impedance points are plotted in real-time on a Smith Chart, using their associated colors.

    - Results Table: A dynamic table displays all recorded impedance data, including motor positions, frequency, impedance values, and color.

    - Data Export: Export the entire impedance history to a CSV file with a custom filename.

    - Clear History: Easily clear all recorded impedance data from both the display and the server's memory.
## Network Setup
Ensure the VNA, Raspberry Pi, and laptop are connected to the same network switch and subnet `10.0.0.X`.
Default VNA IP address: 10.0.0.124
(You can modify this in vna_impedance.py.)

## Accessing the Raspberry Pi
To SSH into the Raspberry Pi:
```bash
ssh csiro@10.0.0.12
```
Password: raspberrypitest

## Step 1: Start the Motor Driver
Run the motor control module:
```bash
python Encoder.py
```

## Step 2: Launch the Flask Web Interface
In a separate terminal, start the web application:
```bash
python app.py
```
Then, open your web browser and go to `<Host IP>:5500`
For example:`localhost:5500`