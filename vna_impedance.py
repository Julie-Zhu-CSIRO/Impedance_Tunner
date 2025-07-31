import pyvisa
import numpy as np
import time

VNA_ADDRESS = "TCPIP0::10.0.0.124::INSTR"

class VNAController:
    """
    Controls a Rohde & Schwarz ZVA8 VNA, maintaining a persistent connection
    for repeated impedance measurements.
    """
    def __init__(self, vna_address: str):
        """
        Initializes the VNA connection and performs initial configuration.

        Args:
            vna_address (str): The VISA resource string or IP address of the VNA.
        """
        self.vna_address = vna_address
        self.rm = pyvisa.ResourceManager()
        self.vna = None

        try:
            self.vna = self.rm.open_resource(self.vna_address)
            self.vna.timeout = 20000  # Increase timeout to 20 sec
            print(f"Connected to VNA: {self.vna.query('*IDN?')}")

            # --- Initial Configuration ---
            print("Performing initial VNA configuration...")

            # Reset the instrument to a known state
            self.vna.write("*RST")
            self.vna.write("*CLS")  # Clear the error queue
            self.vna.write("SYST:DISP:UPD ON")  # Ensure display updates

            # Set up S11 measurement on Channel 1
            self.vna.write("CALC1:PAR:DEL:ALL")
            self.vna.write("CALC1:PAR:SDEF 'CH1_Tr1', 'S11'")
            self.vna.write("DISP:WIND1:STAT ON")
            self.vna.write("DISP:WIND1:TRAC1:FEED 'CH1_Tr1'")
            self.vna.write("SOUR1:POW -15") # Set channel base power to -15 dBm
            self.vna.write("SENS1:BAND 10000") # Set measurement bandwidth to 10 kHz

            # Set to single point sweep mode. Frequency will be set per measurement.
            self.vna.write("SENS1:SWE:POIN 1")
            self.vna.write("CALC1:FORM SMIT") # Set format to Smith Chart (for S11 data retrieval)

            print("VNA initial configuration complete.")

        except pyvisa.VisaIOError as e:
            print(f"Error connecting or configuring VNA: {e}")
            self.vna = None # Ensure vna is None if connection fails
            raise ConnectionError(f"Failed to connect to VNA: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during VNA initialization: {e}")
            self.vna = None
            raise

    def get_impedance(self, target_frequency_hz: float):
        """
        Measures S11 at a specific frequency and returns the impedance.
        Assumes the VNA is already connected and configured.

        Args:
            target_frequency_hz (float): The specific frequency in Hz at which to measure impedance.

        Returns:
            dict: A dictionary containing 'real_impedance' and 'imag_impedance' if successful,
                  otherwise an error message.
        """
        if not self.vna:
            return {"error": "VNA not connected. Please initialize VNAController first."}

        try:
            # Set frequency for the single point measurement
            self.vna.write(f"SENS1:FREQ:STAR {target_frequency_hz}")
            self.vna.write(f"SENS1:FREQ:STOP {target_frequency_hz}")

            # Trigger measurement and wait for completion
            self.vna.write("INIT1:IMM")
            time.sleep(0.5) # Short delay for single point measurement

            # Read S11 data (real and imaginary parts)
            self.vna.write("CALC1:DATA? SDATA")
            raw_data = self.vna.read()

            # Parse the retrieved S11 data
            data_points = np.array(raw_data.split(","), dtype=float).reshape(-1, 2)
            s11_complex = data_points[0, 0] + 1j * data_points[0, 1] # Get the single S11 point

            # Convert to impedance (Z = Z0 * (1 + Γ) / (1 - Γ), assuming Z0 = 50Ω)
            z0 = 50
            impedance = z0 * (1 + s11_complex) / (1 - s11_complex)

            print(f"Impedance at {target_frequency_hz / 1e6} MHz: Real={impedance.real:.2f}, Imag={impedance.imag:.2f}")
            return {"real_impedance": impedance.real, "imag_impedance": impedance.imag}

        except pyvisa.VisaIOError as e:
            print(f"Error communicating with the VNA during measurement: {e}")
            return {"error": f"VNA communication error during measurement: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during VNA measurement: {e}")
            return {"error": f"An unexpected error occurred during measurement: {e}"}

    def close(self):
        """
        Closes the VNA connection.
        """
        if self.vna:
            try:
                self.vna.close()
                print("VNA connection closed.")
            except Exception as e:
                print(f"Error closing VNA connection: {e}")

def test():
    print("Running the VNA Test Procedure")
    vna_controller = None
    try:
        # Use the default VNA_ADDRESS or specify your own
        vna_controller = VNAController(VNA_ADDRESS)

        # Get impedance at 18.5 MHz
        impedance_data = vna_controller.get_impedance(18.5e6)
        print(f"Result for 18.5 MHz: {impedance_data}")

        # Get impedance at another frequency, e.g., 20 MHz
        impedance_data = vna_controller.get_impedance(20e6)
        print(f"Result for 20 MHz: {impedance_data}")

    except ConnectionError as e:
        print(f"Could not establish VNA connection: {e}")
    finally:
        if vna_controller:
            vna_controller.close()

# Example usage (for testing vna_impedance.py independently)
if __name__ == "__main__":
    test()


