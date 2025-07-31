import matplotlib.pyplot as plt
import pysmithchart
import csv

# --- Read Impedance Data from CSV ---
impedances = []
csv_file_path = 'impedance_history.csv'

try:
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Ensure the row has two columns
                try:
                    # Convert string values to floats to create a complex number
                    real_part = float(row[0])
                    imag_part = float(row[1])
                    impedances.append(complex(real_part, imag_part))
                except ValueError:
                    print(f"Warning: Skipping invalid row in CSV: {row}")

except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found.")
    exit()

# --- Plotting the Data ---
if impedances:
    # 1. Define the reference impedance for normalization
    characterisitic_impedance = 50.0

    # 2. Create a matplotlib figure and subplot with the 'smith' projection
    fig, ax = plt.subplots(subplot_kw={'projection': 'smith', 'axes_impedance': characterisitic_impedance})

    # 3. Use the standard ax.plot() function with the NORMALIZED data
    # The 'smith' projection automatically handles complex numbers.
    ax.plot(impedances, marker='o', linestyle='none', label=f"Impedances (Z₀={characterisitic_impedance}Ω)")

    # Add a title and legend
    plt.title("Impedance Smith Chart from CSV")
    plt.legend()

    # Show the plot
    plt.show()
else:
    print("No valid impedance data was read from the CSV file. Nothing to plot.")