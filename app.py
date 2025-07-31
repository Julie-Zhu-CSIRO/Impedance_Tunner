from flask import Flask, send_from_directory, request, flash, jsonify,send_file
import Impedance_Tuning as it
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
    it.motors[n-1].move_motor(value)
    position = it.motors[n-1].request_position()
    print(f'button {n} was pressed, motor move {position} steps')
    return f'{position}'

@app.route('/button/calibrate')
def calibrate_motor():
    it.reset_position()
    print('motor position reseted')
    return f'Reset Position OK'

@app.route('/button/getAllPositions')
def getAllPositions():
    position_all = []
    for i in range(4):
        position_all.append(it.motors[i].request_position())
    print(f'All motors position listed: {position_all}')
    # create comma separated values (csv) string
    positionStr = (',').join(position_all)
    return positionStr

# VNA Impedance Measurement Handler ................................................
@app.route('/get_impedance', methods=['POST'])
def get_impedance_data():
    """
    Flask route to get impedance from VNA at a specified frequency in MHz.
    Receives frequency, motor positions, and dataset color from the frontend via POST request.
    Stores the complete data set in impedance_history.
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

# CSV Export Handler ...............................................................
@app.route('/save_data_csv', methods=['POST'])
def save_data_csv():
    """
    Generates a CSV file from the stored impedance data and sends it for download.
    The filename is provided by the user in the request body.
    """
    data = request.get_json()
    filename = data.get('filename').strip()
    if not filename:
        filename = 'impedance_history'
    if not filename.endswith('.csv'):
        filename += '.csv'

    si = io.StringIO() # Create an in-memory text buffer
    cw = csv.writer(si) # Create a CSV writer for the buffer

    # Write header with all new fields
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
    for row in impedance_history:
        # Ensure motor_positions is a list of 4 elements to avoid index errors
        motor_pos = row.get('motor_positions', ['N/A', 'N/A', 'N/A', 'N/A'])
        cw.writerow([
            row.get('id', ''),
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
        attachment_filename=filename
        # download_name=filename
    )

# Clear the Impedance History ......................................................
@app.route('/clear_impedance_history', methods=['POST'])
def clear_impedance_history():
    """
    Clears the global impedance_history list on the server.
    """
    global impedance_history
    impedance_history = [] # Reset the list to empty
    print("Impedance history cleared on server.")
    return jsonify({"message": "Impedance history cleared successfully."}), 200

#--------------------------------------------------------------------------------
# RUN MAIN
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    initialize_vna_controller() # Initialize VNAController when app start
    app.run(host='0.0.0.0', port=5500, debug=True)
