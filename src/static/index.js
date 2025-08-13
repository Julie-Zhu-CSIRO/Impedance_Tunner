// --- Selectors for Motor Control Elements ---
let inputBox1 = document.querySelector('#numin-1'); // Input field for Motor 1 steps
let inputBox2 = document.querySelector('#numin-2'); // Input field for Motor 2 steps
let inputBox3 = document.querySelector('#numin-3'); // Input field for Motor 3 steps
let inputBox4 = document.querySelector('#numin-4'); // Input field for Motor 4 steps

let spanPos1 = document.querySelector('#pos-1'); // Span to display Motor 1 position
let spanPos2 = document.querySelector('#pos-2'); // Span to display Motor 2 position
let spanPos3 = document.querySelector('#pos-3'); // Span to display Motor 3 position
let spanPos4 = document.querySelector('#pos-4'); // Span to display Motor 4 position

let button_calibrate = document.querySelector('#btn-calibrate'); // Calibrate all motors button

// --- Selectors for VNA Control Elements ---
let vnaFreqInput = document.querySelector('#vna-freq-input'); // Input field for VNA frequency
let btnGetImpedance = document.querySelector('#btn-get-impedance'); // Button to trigger impedance measurement
let realImpedanceSpan = document.querySelector('#real-impedance'); // Span to display real impedance
let imagImpedanceSpan = document.querySelector('#imag-impedance'); // Span to display imaginary impedance
let smithChartCanvas = document.querySelector('#smith-chart-canvas'); // Canvas for Smith Chart
let ctx = smithChartCanvas.getContext('2d'); // 2D rendering context for the canvas
let btnClearHistory = document.querySelector('#btn-clear-history'); // New: Button to clear impedance history

// --- Selectors for Results Panel Elements ---
let impedanceResultsTableBody = document.querySelector('#impedance-results-table tbody'); // Table body for impedance results
let datasetColorSelect = document.querySelector('#dataset-color-select'); // Dropdown for dataset color
let exportFilenameInput = document.querySelector('#export-filename-input'); // Input for custom export filename
let btnExportCustomImpedance = document.querySelector('#btn-export-custom-impedance'); // Button to export with custom filename

// --- Selectors for Parameter Sweep Elements ---
let btnStartSweep = document.querySelector('#btn-start-sweep'); // Button to start a frequency sweep
let sweepImpedanceResultsTableBody = document.querySelector('#impedance-results-table-sweep tbody'); // Table body for sweep impedance results
let realImpedanceSweepSpan = document.querySelector('#real-impedance-sweep'); // Span to display real impedance for sweep
let imagImpedanceSweepSpan = document.querySelector('#imag-impedance-sweep'); // Span to display imaginary impedance for sweep
let smithChartCanvasSweep = document.querySelector('#smith-chart-canvas-sweep'); // Canvas for Sweep Smith Chart
let ctxSweep = smithChartCanvasSweep.getContext('2d'); // 2D rendering context for the sweep canvas
let btnClearHistorySweep = document.querySelector('#btn-clear-history-sweep'); // Button to clear sweep impedance history
let exportFilenameInputSweep = document.querySelector('#export-filename-input-sweep'); // Input for custom sweep export filename
let btnExportCustomImpedanceSweep = document.querySelector('#btn-export-custom-impedance-sweep'); // Button to export sweep with custom filename
let datasetColorSelectSweep = document.querySelector('#dataset-color-select-sweep'); // Dropdown for sweep dataset color

// Global variable to store impedance history
// Each entry will be:
// {
//   motor_positions: [pos1, pos2, pos3, pos4],
//   frequency_mhz: number,
//   real_impedance: number,
//   imag_impedance: number,
//   color: string
// }
let impedanceHistory = [];
let currentDatasetColor = datasetColorSelect.value; // Initialize with default selected color

// Global variable to store sweep impedance history
// Each entry will be:
// {
//   motor_positions: [pos1, pos2, pos3, pos4],
//   frequency_mhz: number,
//   real_impedance: number,
//   imag_impedance: number,
//   color: string
// }
let sweepImpedanceHistory = [];

// --- Helper for custom alert/message box ---
/**
 * Displays a custom message box instead of native alert().
 * @param {string} message - The message to display.
 * @param {string} type - The type of message ('info' or 'error').
 */
function showMessage(message, type = 'info') {
    // Create the message box div
    const messageBox = document.createElement('div');
    messageBox.classList.add('message-box', type); // Add base class and type class
    messageBox.innerHTML = `
        <p>${message}</p>
        <button class="close-btn">OK</button>
    `;
    document.body.appendChild(messageBox); // Append to the body

    // Add event listener to close the message box
    messageBox.querySelector('.close-btn').addEventListener('click', () => {
        messageBox.remove(); // Remove the message box from the DOM
    });
}


// --- Motor Control Functions --------------------------------------------------------------------
/**
 * Sends a command to move a specific motor and updates its position display.
 * @param {number} motorNum - The motor number (1-4).
 * @param {string} value - The number of steps to move.
 */
async function sendMotorCommand(motorNum, value) {
    // Validate input: check if it's a number and within the allowed range
    if (value === "" || isNaN(value) || value < -200 || value > 200) {
        showMessage("Please enter a valid number between -200 and 200.", 'error');
        return; // Exit if validation fails
    }
    // Construct the URL for the Flask endpoint
    let url = `${location.protocol}//${location.host}/button/${motorNum}_${value}`;
    try {
        // Fetch data from the Flask server
        let response = await fetch(url);
        // Get the response text (motor position)
        let data = await response.text();
        console.log(`Motor ${motorNum} response: ${data}`);
        // Update the corresponding motor position display
        document.querySelector(`#pos-${motorNum}`).innerHTML = data;
    } catch (error) {
        // Log and display error if fetch fails
        console.error(`Error moving motor ${motorNum}:`, error);
        showMessage(`Failed to move motor ${motorNum}. Check server connection.`, 'error');
    }
}

// Add keypress event listeners for motor input boxes
// When 'Enter' key is pressed, trigger sendMotorCommand
inputBox1.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMotorCommand(1, inputBox1.value.trim());
    }
});
inputBox2.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMotorCommand(2, inputBox2.value.trim());
    }
});
inputBox3.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMotorCommand(3, inputBox3.value.trim());
    }
});
inputBox4.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMotorCommand(4, inputBox4.value.trim());
    }
});

// Event listener for the Calibrate All Motors button
button_calibrate.addEventListener('click', async () => {
    let url = `${location.protocol}//${location.host}/button/calibrate`;
    try {
        let response = await fetch(url);
        let data = await response.text(); // Expecting "Reset Position OK"
        if (data === "Reset Position OK") {
            // Reset all position displays to 0
            spanPos1.innerHTML = 0;
            spanPos2.innerHTML = 0;
            spanPos3.innerHTML = 0;
            spanPos4.innerHTML = 0;
            showMessage("All motor positions calibrated to 0.");
        } else {
            showMessage("Calibration failed.", 'error');
        }
    } catch (error) {
        console.error("Error calibrating motors:", error);
        showMessage("Failed to calibrate motors. Check server connection.", 'error');
    }
});

// --- VNA Impedance Functions ---------------------------------------------------------------------
/**
 * Draws impedance points on a simplified Smith Chart canvas.
 * @param {HTMLCanvasElement} canvas - The canvas element to draw on.
 * @param {Array} impedancePoints - An array of impedance objects {real_impedance, imag_impedance, color, ...}.
*/
function drawSmithChart(canvas, impedancePoints) {
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.93; // Chart radius, 93% of smaller dimension
    const z0 = 50; // Characteristic impedance (typically 50 Ohms)

    // Clear the entire canvas before drawing to ensure previous points are removed
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw outer circle (representing |Gamma|=1, normalized impedance 1+j0)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#95a5a6'; // Light grey color
    ctx.lineWidth = 1; // Thin line
    ctx.stroke();

    // Draw horizontal line (real axis of the Smith Chart)
    ctx.beginPath();
    ctx.moveTo(centerX - radius, centerY);
    ctx.lineTo(centerX + radius, centerY);
    ctx.strokeStyle = '#95a5a6';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Iterate over each impedance point in the history and plot it
    impedancePoints.forEach((impedance, index) => {
        const r = impedance.real_impedance;
        const x = impedance.imag_impedance;

        // Normalize impedance: z = R/Z0 + jX/Z0
        const r_norm = r / z0;
        const x_norm = x / z0;

        // Convert normalized impedance to reflection coefficient Gamma (Γ)
        // Γ = (z - 1) / (z + 1)
        const denominator = (r_norm + 1) * (r_norm + 1) + x_norm * x_norm;
        const gamma_real = ((r_norm - 1) * (r_norm + 1) + x_norm * x_norm) / denominator;
        const gamma_imag = (2 * x_norm) / denominator;

        // Map Gamma coordinates to canvas pixel coordinates
        // Smith Chart center (Gamma = 0+j0) maps to (centerX, centerY) on canvas
        // Radius of Smith Chart (Gamma = 1) maps to 'radius' on canvas
        const plotX = centerX + gamma_real * radius;
        const plotY = centerY - gamma_imag * radius; // Y-axis is inverted in canvas

        // Draw the impedance point
        ctx.beginPath();
        // Use the selected plotColor for all points
        ctx.arc(plotX, plotY, 4, 0, 2 * Math.PI); // Point size
        ctx.fillStyle = impedance.color; // Use the stored color for each point
        ctx.fill();
        ctx.strokeStyle = '#333'; // A darker stroke for contrast
        ctx.lineWidth = 1;
        ctx.stroke();

        // Optionally, add text label for the latest point or all points
        if (index === impedancePoints.length - 1) { // Only label the latest point
            ctx.fillStyle = '#2c3e50';
            ctx.font = '12px Arial';
            ctx.fillText(`Z: ${r.toFixed(2)} + j${x.toFixed(2)}`, plotX + 10, plotY - 10);
        }
    });
}

// Event listener for the Get Impedance button
btnGetImpedance.addEventListener('click', async () => {
    // Get the frequency from the input field and parse it as a float
    let frequencyMhz = parseFloat(vnaFreqInput.value.trim());

    // Validate the frequency input
    if (isNaN(frequencyMhz) || frequencyMhz <= 0) {
        showMessage("Please enter a valid positive frequency in MHz.", 'error');
        return; // Exit if validation fails
    }

    // Get current motor positions
    const motorPositions = [
        spanPos1.innerHTML,
        spanPos2.innerHTML,
        spanPos3.innerHTML,
        spanPos4.innerHTML
    ];

    // Get the selected dataset color
    const datasetColor = datasetColorSelect.value;

    // Update display to show "Measuring..." state
    realImpedanceSpan.innerHTML = 'Measuring...';
    imagImpedanceSpan.innerHTML = 'Measuring...';

    // Construct the URL for the Flask endpoint to get impedance
    let url = `${location.protocol}//${location.host}/get_impedance`;
    try {
        // Fetch impedance data from the Flask server using POST
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                frequency_mhz: frequencyMhz,
                motor_positions: motorPositions,
                dataset_color: datasetColor
            })
        });
        let data = await response.json(); // Parse the JSON response

        // Check if the response was successful (HTTP status 200-299)
        if (response.ok) {
            // Update the impedance display spans
            realImpedanceSpan.innerHTML = data.real_impedance.toFixed(2); // Format to 2 decimal places
            imagImpedanceSpan.innerHTML = data.imag_impedance.toFixed(2);

            // Add the new data point (which includes all details) to the client-side history
            impedanceHistory.push(data);

            // Update the impedance table and redraw the Smith chart with all points
            updateImpedanceTable();
            drawSmithChart(smithChartCanvas, impedanceHistory); // Pass the entire history to draw

        } else {
            // Handle error response from Flask (e.g., VNA not connected)
            realImpedanceSpan.innerHTML = 'Error';
            imagImpedanceSpan.innerHTML = 'Error';
            showMessage(`Error: ${data.error || 'Unknown error fetching impedance.'}`, 'error');
        }
    } catch (error) {
        // Handle network errors or other unexpected issues during fetch
        console.error("Error fetching impedance:", error);
        realImpedanceSpan.innerHTML = 'Error';
        imagImpedanceSpan.innerHTML = 'Error';
        showMessage("Failed to fetch impedance. Check VNA connection or server.", 'error');
    }
});

// --- Results Panel Functions ----------------------------------------------------------------------

/**
 * Updates the impedance results table with the data from impedanceHistory.
 */
function updateImpedanceTable() {
    impedanceResultsTableBody.innerHTML = ''; // Clear existing rows

    if (impedanceHistory.length === 0) {
        impedanceResultsTableBody.innerHTML = '<tr><td colspan="4">No impedance data yet.</td></tr>';
        return;
    }

    impedanceHistory.forEach((data, index) => {
        const row = impedanceResultsTableBody.insertRow();
        row.insertCell().textContent = index + 1;
        row.insertCell().textContent = data.motor_positions.join(', '); // Motor positions
        row.insertCell().textContent = data.frequency_mhz.toFixed(1); // Frequency
        row.insertCell().textContent = data.real_impedance.toFixed(2);
        row.insertCell().textContent = data.imag_impedance.toFixed(2);

        // Create a colored dot for the color column
        const colorCell = row.insertCell();
        const colorDot = document.createElement('span');
        colorDot.classList.add('color-dot');
        colorDot.style.backgroundColor = data.color;
        colorCell.appendChild(colorDot);
    });

    // Scroll to the bottom of the table to show the latest entry
    impedanceResultsTableBody.parentElement.scrollTop = impedanceResultsTableBody.parentElement.scrollHeight;
}

// Event listener for the Data Set Color dropdown
datasetColorSelect.addEventListener('change', (event) => {
    currentDatasetColor = event.target.value; // Update the global color variable
});

// Event listener for the custom export button
btnExportCustomImpedance.addEventListener('click', async () => {
    const filename = exportFilenameInput.value;
    if (!filename) {
        showMessage('Please enter a filename for export.', 'error');
        return;
    }
    try {
        const response = await fetch('/save_data_csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename })
        });

        if (response.ok) {
            // Trigger file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showMessage('CSV file generated and downloaded!');
        } else {
            const errorText = await response.text();
            showMessage(`Error saving CSV: ${errorText}`, `error`);
        }
    } catch (error) {
        console.error('Error saving CSV:', error);
        showMessage('Failed to save CSV. Please try again.', `error`);
    }
});

// Event listener for the Clear History button
btnClearHistory.addEventListener('click', async () => {
    try {
        const response = await fetch('/clear_impedance_history', {
            method: 'POST' // Use POST for state-changing operations
        });

        if (response.ok) {
            impedanceHistory = []; // Clear client-side history
            updateImpedanceTable(); // Update table to show no data
            drawSmithChart(smithChartCanvas,impedanceHistory); // Clear Smith Chart
            showMessage('Impedance history cleared successfully!');
        } else {
            const errorText = await response.text();
            showMessage(`Error clearing history: ${errorText}`, 'error');
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        showMessage('Failed to clear history. Please try again.', 'error');
    }
});


// --- Sweep Parameter Functions ----------------------------------------------------------------------
// Event listener for the Start Sweep button
btnStartSweep.addEventListener('click', async () => {
    startSweep();
});

// Starts a frequency sweep.
async function startSweep() {
    // Get the selected motor index from the dropdown
    const sweepMotorSelect = document.querySelector('#sweep-motor-select');
    const selectedMotorIndex = sweepMotorSelect.value; // Get the value directly

    // Get the other sweep parameters
    const startValue = parseFloat(document.querySelector('#sweep-start-value').value);
    const stopValue = parseFloat(document.querySelector('#sweep-stop-value').value);
    const stepSize = parseFloat(document.querySelector('#sweep-step-size').value);
    const frequencyMhz = parseFloat(document.querySelector('#sweep-freq-input').value);

    realImpedanceSweepSpan.innerHTML = 'Measuring...';
    imagImpedanceSweepSpan.innerHTML = 'Measuring...';

    let url = `${location.protocol}//${location.host}/start_sweep`;
    try {
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Indicate that the body is JSON
            },
            body: JSON.stringify({
                motor_index: selectedMotorIndex,
                start_value: startValue,
                stop_value: stopValue,
                step_size: stepSize,
                frequency_mhz: frequencyMhz
                // Add other sweep parameters here as needed by your Flask endpoint
            })
        });

        if (response.ok) {
            showMessage('Frequency sweep started successfully!');
        } else {
            const errorText = await response.text();
            showMessage(`Error starting sweep: ${errorText}`, 'error');
        }
    } catch (error) {
        console.error('Error starting sweep:', error);
        showMessage('Failed to start sweep. Please try again.', 'error');
    }
}

/**
 * Clears the sweep impedance history and updates the display.
 */
async function btnClearSweepHistory() {
    sweepImpedanceHistory = []; // Clear client-side history
    updateSweepImpedanceTable(); // Update table to show no data
    drawSmithChart(smithChartCanvasSweep, sweepImpedanceHistory); // Clear Smith Chart
    showMessage('Sweep impedance history cleared successfully!');
}

/**
 * Updates the sweep impedance results table with the data from sweepImpedanceHistory.
 */
function updateSweepImpedanceTable() {
    sweepImpedanceResultsTableBody.innerHTML = ''; // Clear existing rows

    if (sweepImpedanceHistory.length === 0) {
        sweepImpedanceResultsTableBody.innerHTML = '<tr><td colspan="6">No sweep impedance data yet.</td></tr>';
        return;
    }

    sweepImpedanceHistory.forEach((data, index) => {
        const row = sweepImpedanceResultsTableBody.insertRow();
        row.insertCell().textContent = index + 1;
        row.insertCell().textContent = data.motor_positions ? data.motor_positions.join(', ') : 'N/A'; // Motor positions (handle potential absence)
        row.insertCell().textContent = data.frequency_mhz.toFixed(1); // Frequency
        row.insertCell().textContent = data.real_impedance.toFixed(2);
        row.insertCell().textContent = data.imag_impedance.toFixed(2);

        // Create a colored dot for the color column
        const colorCell = row.insertCell();
        const colorDot = document.createElement('span');
        colorDot.classList.add('color-dot');
        colorDot.style.backgroundColor = data.color;
        colorCell.appendChild(colorDot);
    });

    // Scroll to the bottom of the table to show the latest entry
    sweepImpedanceResultsTableBody.parentElement.scrollTop = sweepImpedanceResultsTableBody.parentElement.scrollHeight;
}

/**
 * Handles the export of sweep impedance data to CSV.
 */
async function handleSweepExport() {
    const filename = exportFilenameInputSweep.value;
    if (!filename) {
        showMessage('Please enter a filename for sweep export.', 'error');
        return;
    }
    try {
        // You will need a backend endpoint that specifically saves the sweep history.
        // Assuming you have a /save_sweep_data_csv endpoint
        const response = await fetch('/save_sweep_data_csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename, data: sweepImpedanceHistory }) // Send the history data
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
// Event listener for the Clear History button
btnClearHistory.addEventListener('click', async () => {
    try {
        const response = await fetch('/clear_impedance_history', {
            method: 'POST' // Use POST for state-changing operations
        });

        if (response.ok) {
            impedanceHistory = []; // Clear client-side history
            updateImpedanceTable(); // Update table to show no data
            drawSmithChart(smithChartCanvas, impedanceHistory); // Clear Smith Chart
            showMessage('Impedance history cleared successfully!');
        } else {
            const errorText = await response.text();
            showMessage(`Error clearing history: ${errorText}`, 'error');
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        showMessage('Failed to clear history. Please try again.', 'error');
    }
});

            showMessage('Sweep CSV file generated and downloaded!');
        } else {
            const errorText = await response.text();
            showMessage(`Error saving sweep CSV: ${errorText}`, `error`);
        }
    } catch (error) {
        console.error('Error saving sweep CSV:', error);
        showMessage('Failed to save sweep CSV. Please try again.', `error`);
    }
}

// Event listener for the custom sweep export button
btnExportCustomImpedanceSweep.addEventListener('click', handleSweepExport);

// --- Initial Page Load Function ---
/**
 * Initializes the page by fetching and displaying the current motor positions.
 * and fetching/drawing the impedance history.
 */
async function initPage() {
    // Construct the URL to get all encoder positions
    let url = `${location.protocol}//${location.host}/button/getAllPositions`;
    try {
        let response = await fetch(url);
        let data = await response.text(); // Response is a comma-separated string
        let positions = data.split(','); // Split the string into an array of positions
        console.log("Initial motor positions:", positions);
        // Set the initial positions on the HTML spans
        spanPos1.innerHTML = positions[0];
        spanPos2.innerHTML = positions[1];
        spanPos3.innerHTML = positions[2];
        spanPos4.innerHTML = positions[3];
    } catch (error) {
        console.error("Error fetching initial motor positions:", error);
        showMessage("Failed to load initial motor positions.", 'error');
    }

    // Initial draw of Smith Chart (will be empty if no history)
    drawSmithChart(smithChartCanvas,impedanceHistory);
    // Initial update of impedance table (will show "No data" if empty)
    updateImpedanceTable();
}

// Call initPage() when the script loads to set initial motor positions
initPage();
