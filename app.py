from flask import Flask, send_from_directory, request, flash, jsonify,send_file
# import Impedance_Tuning as it
from vna_impedance import VNAController, VNA_ADDRESS

import csv # Import csv module for handling CSV files
import io

# --- Flask Application Setup ---
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg','gif'}
app = Flask(__name__,static_folder='src/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global instance for VNAController
vna:VNAController = None

# Global list to store impedance history
# Each entry will be a dictionary containing:
# 'motor_positions': List of current positions for motors 1-4
# 'frequency_mhz': Frequency at which impedance was measured
# 'real_impedance': Real part of the measured impedance
# 'imag_impedance': Imaginary part of the measured impedance
# 'color': Color associated with the data point for plotting/display
impedance_history = []

# Global list to store impedance history for parameter sweeps
sweep_history = []

# Dummy motor positions for simulation if Impedance_Tuning is not available
simulated_motor_positions = [0, 0, 0, 0]

#--------------------------------------------------------------------------------
# INIT VNA
#--------------------------------------------------------------------------------

# Initialize VNAController when app start .......................................
# @app.before_first_request
def initialize_vna_controller():
    """
    Initializes the VNAController global instance.
    This function is called when the Flask application starts.
    """
    global vna
    try:
        vna = VNAController(VNA_ADDRESS)
        print("VNA Controller initialized successfully.")
    except ConnectionError as e:
        print(f"Application failed to initialize VNA: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during VNA controller initialization: {e}")

# Ensure VNA connection is closed when the app context tears down
# @app.teardown_appcontext
# def close_vna_connection(exception=None):
#     global vna
#     if vna:
#         vna.close()
#         vna = None # Clear the instance

#--------------------------------------------------------------------------------
# ROUTES
#--------------------------------------------------------------------------------

# Web Server Resource Handlers ................................................
@app.route('/')
def home():
    """Serves the main HTML page."""
    return send_from_directory('src/', 'index.html')

@app.route('/static/<path:fileName>')
def staticFileHandler(fileName):
    """Serves static files (CSS, JS) from the 'static' directory."""
    print(f"attempt to access static file: static/{fileName}")
    return send_from_directory('static', fileName)

# Motor Control Event Handlers .....................................................
@app.route('/button/<int:n>_<int(signed=True):value>')
def doButtonThing(n,value):
    # it.motors[n-1].move_motor(value)
    position = it.motors[n-1].request_position()
    print(f'button {n} was pressed, motor move {position} steps')
    return f'{position}'

@app.route('/button/calibrate')
def calibrate_motor():
    # it.reset_position()
    print('motor position reseted')
    return f'Reset Position OK'

@app.route('/button/getAllPositions')
def getAllPositions():
    position_all = []
    # for i in range(4):
    #     position_all.append(it.motors[i].request_position())
    print(f'All motors position listed: {position_all}')
    # create comma separated values (csv) string
    positionStr = (',').join(position_all)
    return positionStr

# VNA Impedance Measurement Handler (Single Measurement Tab) ......................
@app.route('/get_impedance', methods=['POST'])
def get_impedance_data():
    """
    Flask route to get impedance from VNA at a specified frequency in MHz.
    Receives frequency, motor positions, and dataset color from the frontend via POST request.
    Stores the complete data set in impedance_history.
    Used by the 'Motor Control' tab.
    """
    data = request.get_json() # Get JSON data from the request body
    frequency_mhz = data.get('frequency_mhz')
    motor_positions = data.get('motor_positions')
    dataset_color = data.get('dataset_color')

    if frequency_mhz is None or motor_positions is None or dataset_color is None:
        return jsonify({"error": "Missing data: frequency, motor positions, or color."}), 400
    
    target_frequency_hz = frequency_mhz * 1e6 # Convert MHz to Hz
    print(f"Request to get impedance at {frequency_mhz} MHz ({target_frequency_hz} Hz) "
          f"with motor positions {motor_positions} and color {dataset_color}")

    global vna, impedance_history
    impedance_data_from_vna = {}

    if not vna:
        # Simulate VNA response if not initialized (for testing without hardware)
        import random
        real_imp = random.uniform(10, 100)
        imag_imp = random.uniform(-50, 50)
        impedance_data_from_vna = {'real_impedance': real_imp, 'imag_impedance': imag_imp}
        print(f"Simulated impedance: {impedance_data_from_vna}")
    else:
        # Attempt to get actual impedance from VNA
        impedance_data_from_vna = vna.get_impedance(target_frequency_hz)

    if "error" in impedance_data_from_vna:
        # If VNA returned an error, send it back to the client
        return jsonify(impedance_data_from_vna), 500
    else:
        # Construct the full data point to save in history
        new_data_point = {
            'motor_positions': motor_positions,
            'frequency_mhz': frequency_mhz,
            'real_impedance': impedance_data_from_vna['real_impedance'],
            'imag_impedance': impedance_data_from_vna['imag_impedance'],
            'color': dataset_color
        }
        impedance_history.append(new_data_point) # Add the new data point to the history list
        return jsonify(new_data_point) # Return the newly added data point

# CSV Export Handler (Single Measurement Tab) .....................................
@app.route('/save_data_csv', methods=['POST'])
def save_data_csv():
    """
    Generates a CSV file from the stored single measurement impedance data.
    The filename is provided by the user.
    """
    data = request.get_json()
    filename = data.get('filename', 'impedance_history').strip()
    if not filename.endswith('.csv'):
        filename += '.csv'

    si = io.StringIO() # Create an in-memory text buffer
    cw = csv.writer(si) # Create a CSV writer for the buffer

    # Write header with all fields
    cw.writerow([
        'Data Number',
        'Motor 1 Position',
        'Motor 2 Position',
        'Motor 3 Position',
        'Motor 4 Position',
        'Frequency (MHz)',
        'Real Impedance (Ohms)',
        'Imaginary Impedance (Ohms)',
        'Color'
    ])

    # Write data rows
    for i, row in enumerate(impedance_history):
        # Ensure motor_positions is a list of 4 elements to avoid index errors
        motor_pos = row.get('motor_positions', ['N/A', 'N/A', 'N/A', 'N/A'])
        # Ensure motor_pos has exactly 4 elements, pad with 'N/A' if needed
        while len(motor_pos) < 4:
            motor_pos.append('N/A')

        cw.writerow([
            i + 1, # Data Number (row index + 1)
            motor_pos[0],
            motor_pos[1],
            motor_pos[2],
            motor_pos[3],
            row.get('frequency_mhz', ''),
            row.get('real_impedance', ''),
            row.get('imag_impedance', ''),
            row.get('color', '')
        ])

    output = io.BytesIO(si.getvalue().encode('utf-8')) # Encode string to bytes
    output.seek(0) # Go to the beginning of the stream

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# Clear the Impedance History (Single Measurement Tab) .........................
@app.route('/clear_impedance_history', methods=['POST'])
def clear_impedance_history():
    """
    Clears the global impedance_history list on the server.
    Used by the 'Motor Control' tab.
    """
    global impedance_history
    impedance_history = [] # Reset the list to empty
    print("Single measurement impedance history cleared on server.")
    return jsonify({"message": "Impedance history cleared successfully."}), 200

# Parameter Sweep Handlers .....................................................
@app.route('/start_sweep', methods=['POST'])
def start_sweep():
    """
    Flask route to start a parameter sweep.
    Receives motor index, start/stop values, step size, and frequency from frontend.
    Performs the sweep and returns the collected data.
    """
    data = request.get_json()
    motor_index = data.get('motor_index')
    start_value = data.get('start_value')
    stop_value = data.get('stop_value')
    step_size = data.get('step_size')
    frequency_mhz = data.get('frequency_mhz')
    dataset_color = data.get('dataset_color', '#3498db') # Default color for sweep

    if any(val is None for val in [motor_index, start_value, stop_value, step_size, frequency_mhz]):
        return jsonify({"error": "Missing parameter sweep configuration."}), 400

    target_frequency_hz = frequency_mhz * 1e6 # Convert MHz to Hz

    global sweep_history, simulated_motor_positions
    sweep_history = [] # Clear previous sweep data

    print(f"Starting sweep for motor {motor_index+1}: {start_value} to {stop_value} with step {step_size}"
          f" at {frequency_mhz} MHz.")

    try:
        # Move to start position
        #it.motors[motor_index-1].move_motor(start_value)

        current_position = it.motors[motor_index-1].request_position()
        # Adjust stop_value check to handle both increasing and decreasing sweeps
        is_increasing = stop_value >= start_value

        # Loop through positions
      
        # Let's calculate steps and loop for simplicity and accuracy with step_size
        # This assumes step_size is consistent in motor units.
        if is_increasing and step_size <= 0:
             return jsonify({"error": "Step size must be positive for increasing sweep."}), 400
        if not is_increasing and step_size >= 0:
             return jsonify({"error": "Step size must be negative for decreasing sweep."}), 400

        i = 0;
        while current_position < stop_value:
            it.motors[motor_index-1].move_motor(step_size)
            current_position = it.motors[motor_index-1].request_position() # Get actual position after move

            # Get impedance data
            impedance_data_from_vna = vna.get_impedance(target_frequency_hz)

            if "error" in impedance_data_from_vna:
                print(f"Error getting impedance at position {current_position_actual}: {impedance_data_from_vna['error']}")
                # Decide how to handle VNA errors during sweep: skip point, stop sweep, etc.
                # For now, we'll just continue with the sweep but log the error.
                continue # Skip this data point if VNA error occurs

            data_point = {
                'id': i + 1, # Data point number in the sweep
                'motor_positions': current_positions,
                'frequency_mhz': frequency_mhz,
                'real_impedance': impedance_data_from_vna['real_impedance'],
                'imag_impedance': impedance_data_from_vna['imag_impedance'],
                'color': dataset_color # Use the selected dataset color
            }
            sweep_history.append(data_point)
            print(f"Measured at pos {current_position_actual}: R={data_point['real_impedance']:.2f}, X={data_point['imag_impedance']:.2f}")

            i = i+1
        print("Sweep finished.")
        return jsonify(sweep_history) # Return the collected sweep data

    except Exception as e:
        print(f"An error occurred during the sweep: {e}")
        return jsonify({"error": f"An error occurred during the sweep: {e}"}), 500


@app.route('/save_sweep_results_csv', methods=['POST'])
def save_sweep_results_csv():
    """
    Generates a CSV file from the stored sweep impedance data.
    The filename is provided by the user.
    """
    data = request.get_json()
    filename = data.get('filename', 'sweep_results').strip()
    if not filename.endswith('.csv'):
        filename += '.csv'

    si = io.StringIO() # Create an in-memory text buffer
    cw = csv.writer(si) # Create a CSV writer for the buffer

    # Write header with all fields
    cw.writerow([
        'Data Number',
        'Motor Position',
        'Frequency (MHz)',
        'Real Impedance (Ohms)',
        'Imaginary Impedance (Ohms)',
        'Color'
    ])

    # Write data rows from sweep_history
    for i, row in enumerate(sweep_history):
        motor_pos = row.get('motor_positions', ['N/A', 'N/A', 'N/A', 'N/A'])
         # Ensure motor_pos has exactly 4 elements, pad with 'N/A' if needed
        while len(motor_pos) < 4:
            motor_pos.append('N/A')

        cw.writerow([
            row.get('id', i + 1), # Use stored id or row index + 1
            row.get('motor_positions',''),
            row.get('frequency_mhz', ''),
            row.get('real_impedance', ''),
            row.get('imag_impedance', ''),
            row.get('color', '')
        ])

    output = io.BytesIO(si.getvalue().encode('utf-8')) # Encode string to bytes
    output.seek(0); # Go to the beginning of the stream

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/clear_sweep_history', methods=['POST'])
def clear_sweep_history():
    """
    Clears the global sweep_history list on the server.
    Used by the 'Parameter Sweep' tab.
    """
    global sweep_history
    sweep_history = [] # Reset the list to empty
    print("Parameter sweep history cleared on server.")
    return jsonify({"message": "Parameter sweep history cleared successfully."}), 200

#--------------------------------------------------------------------------------
# RUN MAIN
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    initialize_vna_controller() # Initialize VNAController when app start
    app.run(host='0.0.0.0', port=5500, debug=True)
