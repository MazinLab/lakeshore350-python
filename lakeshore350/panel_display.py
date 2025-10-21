"""

Outlines functions that can be called through CLI to control lakeshore front panel 

Includes functionality to query input names and change input names

Provides:
- show_display(port='/dev/ttyUSB2'): open serial, query INNAME? D1, print the result, close serial.
"""
import serial
import time


def show_display(port: str = '/dev/ttyUSB2', input_name: str = 'D1'):
    """Query the panel display for a named input and print the returned name.

    If input_name == 'ALL' the function queries a sensible set of inputs
    (A, B, C, D1..D5) and prints each response.
    """
    inputs = []
    if str(input_name).upper() == 'ALL':
        inputs = ['A', 'B', 'C', 'D1', 'D2', 'D3', 'D4', 'D5']
    else:
        inputs = [input_name]

    ser = None
    try:
        ser = serial.Serial(port=port, baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)
        for inp in inputs:
            try:
                cmd = f'INNAME? {inp}\n'.encode('ascii')
                ser.write(cmd)
                time.sleep(0.2)
                resp = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"Input Display Name {inp}: {resp}")
            except Exception as e:
                print(f"Failed to query {inp}: {e}")
    except Exception as e:
        print(f"Failed to open serial port {port}: {e}")
    finally:
        try:
            if ser is not None:
                ser.close()
        except Exception:
            pass


if __name__ == '__main__':
    # simple CLI when run directly
    show_display()


def set_name(port: str = '/dev/ttyUSB2', input_name: str = 'D5', name: str = 'TEST_NAME'):
    """Set the panel display name for a given input.

    This sends the command: INNAME <input>,"<name>"
    """
    ser = None
    try:
        ser = serial.Serial(port=port, baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)
        cmd_str = f'INNAME {input_name},"{name}"\n'
        cmd = cmd_str.encode('ascii')
        ser.write(cmd)
        time.sleep(0.2)
        # Confirm command was sent
        print(f"Set name command sent for {input_name} -> '{name}'")
    except Exception as e:
        print(f"Failed to open serial port {port}: {e}")
    finally:
        try:
            if ser is not None:
                ser.close()
        except Exception:
            pass


def get_display_name(port: str = '/dev/ttyUSB2', input_name: str = 'D1') -> str:
    """Query the panel for INNAME? <input> and return the name (or None on error).

    Returns the stripped response string or None if there was an error or no response.
    """
    ser = None
    try:
        ser = serial.Serial(port=port, baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)
        cmd = f'INNAME? {input_name}\n'.encode('ascii')
        ser.write(cmd)
        time.sleep(0.2)
        resp = ser.readline().decode('ascii', errors='ignore').strip()
        return resp if resp else None
    except Exception:
        return None
    finally:
        try:
            if ser is not None:
                ser.close()
        except Exception:
            pass
