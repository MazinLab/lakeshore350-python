
#!/usr/bin/env python3
"""
Check Lakeshore 350 Front Panel Display Status (direct serial, no GL7Controller)
"""

import argparse
import serial
import time
import string

def send_command(ser, command, timeout=0.2):
    ser.write((command + '\r\n').encode())
    ser.flush()
    time.sleep(timeout)
    response = ser.read_all().decode(errors='ignore').strip()
    return response


def check_front_panel_display(port="/dev/ttyUSB2"):
    """
    Queries all inputs (A, B, C, D1-D5) on the Lake Shore 350
    and prints their front panel labels (actual text).
    Returns a dictionary mapping input -> label.
    """
    inputs = ["A", "B", "C", "D1", "D2", "D3", "D4", "D5"]
    input_labels = {}

    try:
        with serial.Serial(port, baudrate=57600, timeout=2) as ser:
            for inp in inputs:
                # Flush any leftover bytes to avoid mixing responses
                ser.reset_input_buffer()
                
                # Send the INNAME? command, using only carriage return (\r)
                command = f"INNAME? {inp}\r"
                ser.write(command.encode('ascii'))

                # Wait long enough for the 350 to respond
                time.sleep(0.5)

                # Read until CR (\r)
                raw = ser.read_until(b'\r')

                # Fallback: read any remaining bytes
                if not raw:
                    time.sleep(0.1)
                    raw = ser.read_all()

                # Decode as ASCII and filter out non-printable characters
                decoded = raw.decode('ascii', errors='ignore')
                cleaned = ''.join(ch for ch in decoded if ch in string.printable).strip()

                # If the result is empty or looks like numeric junk, mark as None
                if not cleaned or cleaned.isdigit():
                    cleaned = "None"

                input_labels[inp] = cleaned
                print(f"Input {inp}: {cleaned}")

        return input_labels

    except Exception as e:
        print(f"Error checking display: {e}")
        return None
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Lakeshore 350 front panel display")
    parser.add_argument("--port", default="/dev/ttyUSB2", help="Serial port")
    args = parser.parse_args()
    check_front_panel_display(args.port)
