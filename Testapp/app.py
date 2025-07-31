# app.py
from flask import Flask, request, jsonify, render_template, send_file
import io
import csv

app = Flask(__name__)

# In a real application, you might use a database.
# For simplicity, we'll store data in a list in memory.
# This data will reset if the server restarts.
impedance_data = []
data_counter = 0

@app.route('/')
def index():
    """
    Renders the main HTML page.
    """
    return render_template('index.html')

@app.route('/add_impedance', methods=['POST'])
def add_impedance():
    """
    Receives impedance data (real and imaginary parts) from the frontend,
    adds it to the in-memory list, and returns the updated data.
    """
    global data_counter
    try:
        data = request.get_json()
        real_part = float(data.get('real'))
        imaginary_part = float(data.get('imaginary'))

        data_counter += 1
        impedance_data.append({
            'id': data_counter,
            'real': real_part,
            'imaginary': imaginary_part
        })
        # Return the newly added row data so the frontend can append it
        return jsonify({
            'success': True,
            'id': data_counter,
            'real': real_part,
            'imaginary': imaginary_part
        })
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': f'Invalid input: {e}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {e}'}), 500

@app.route('/get_all_data', methods=['GET'])
def get_all_data():
    """
    Returns all currently stored impedance data.
    This is useful for initial table population or refreshing.
    """
    return jsonify(impedance_data)

@app.route('/save_data_csv', methods=['POST'])
def save_data_csv():
    """
    Generates a CSV file from the stored impedance data and sends it for download.
    The filename is provided by the user in the request body.
    """
    data = request.get_json()
    filename = data.get('filename', 'impedance_data').strip()
    if not filename:
        filename = 'impedance_data'
    if not filename.endswith('.csv'):
        filename += '.csv'

    si = io.StringIO()
    cw = csv.writer(si)

    # Write header
    cw.writerow(['Data Number', 'Real Part', 'Imaginary Part'])

    # Write data rows
    for row in impedance_data:
        cw.writerow([row['id'], row['real'], row['imaginary']])

    output = io.BytesIO(si.getvalue().encode('utf-8'))
    output.seek(0) # Go to the beginning of the stream

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # Run the Flask app in debug mode.
    # In a production environment, you would use a production-ready WSGI server.
    app.run(debug=True)
