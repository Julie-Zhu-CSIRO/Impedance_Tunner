# Motor Control & VNA Web Interface

This project provides a Python Flask web application that integrates two key components:
- A Motor Driver module
- VNA (Vector Network Analyzer) control

The web interface allows for both individual motor control and impedance measurements, as well as automated parameter sweeps across motor positions while taking VNA readings.

## Features

- **Motor Control**: Control up to four motors, move them by specified steps, and calibrate their positions.

- **VNA Impedance Measurement**: Get real and imaginary impedance values from a VNA at a specified frequency.

- **Parameter Sweep**: Automate the process of sweeping a selected motor through a range of positions and collecting VNA impedance data at each step.

- **GUI**: A web-based graphical user interface with two main tabs:
    - **Motor Control**: For individual motor movement and single VNA measurements.
    - **Parameter Sweep**: For configuring and running automated motor sweeps and viewing the collected impedance data.

- **Enhanced Impedance History**: Each impedance measurement logs comprehensive data, including motor positions, frequency, impedance values, and color.

- **Smith Chart Visualization**: All measured impedance points (both single measurements and sweep results) are plotted in real-time on a Smith Chart, using their associated colors.

- **Results Table**: Dynamic tables in both tabs display the recorded impedance data.

- **Data Export**: Export the impedance history (either single measurements or sweep results) to a CSV file with a custom filename.

- **Clear History**: Easily clear the recorded impedance data from the display and the server's memory for each respective tab.

## Network Setup

Ensure the VNA, Raspberry Pi, and laptop are connected to the same network switch and subnet `10.0.0.X`.

Default VNA IP address: 10.0.0.124 (You can modify this in `vna_impedance.py`.)

## Accessing the Raspberry Pi

To SSH into the Raspberry Pi:

```bash
ssh csiro@10.0.0.12
```

Password: raspberrypitest

## Step 1: Start the Motor Driver (If applicable)

If you have a separate motor control script (e.g., `Encoder.py` or integrated into `Impedance_Tuning.py`), run it first:

```bash
python Encoder.py
```

*(Note: The provided `app.py` includes simulated motor control functions if a dedicated motor driver module is not available or integrated.)*

## Step 2: Launch the Flask Web Interface

In a separate terminal, start the web application:

```bash
python app.py
```

Then, open your web browser and go to `<Host IP>:5500`
For example: `localhost:5500`
