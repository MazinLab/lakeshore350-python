#!/usr/bin/env python3
"""
This file handles all of the channel/input reading functionality for the lakeshore350 

All serial commands for reading voltage, resistance, and temperature are located here. 

Main Functions: 
- read_temperature(): Main function - returns temp in K or resistance in Ω
- read_sensor(): Direct sensor reading (Ω for heads, V for pumps)
- read_voltage(): Direct voltage reading in V
- send_command(): Sends command over serial 

Lakeshore Hardware:
- Input A (3-head resistance thermometer, requires calibration in software)
- Input B (1K GGG, not sure what kind of thermometry)
- Input C (4-head resistance thermometer, requires calibration in software)
- Channel D1 (Film-burner diode, not currently using)
- Channel D2 (4K stage diode, calibrated directly on the lakeshore, curve 21)
- Channel D3 (50K stage diode, calibrated directly on the lakeshore, curve 22, not working rn)
- Channel D4 (3-pump diode, requires calibration in software)
- Channel D5 (4-pump diode, requires calibration in software )

***
Note, D1-D5 are referred to as channels but they are technically special inputs. 
Channels 1-8 read the exact same temp as input A. They're not being used 
***

"""

import serial
import time

class TemperatureReader:
    """
    Usage Examples:
        temp_reader = TemperatureReader()
        # Temperature readings (returns float in Kelvin or "T_OVER")
        temp = temp_reader.read_temperature(5)      # Reads Channel 5
        temp = temp_reader.read_temperature('D3')   # Reads Channel D3
        temp = temp_reader.read_temperature('B')    # Reads Input B
        # Sensor readings (returns float in Ohms or Volts or "R_OVER")
        sensor = temp_reader.read_sensor('A')  # Input A (3-head), yields resistance in Ohms
        sensor = temp_reader.read_sensor('D5') # Channel D5 (4-pump), yields voltage in Volts
        # Serial Commands Used:
        #   KRDG? - Kelvin temperature reading
        #   SRDG? - Resistance reading
        #   RDGST? - Status reading (detects over-range conditions)
    """

    def __init__(self, port="/dev/ttyUSB2", baudrate=57600, timeout=2):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=7,
            parity='O',  # Odd parity
            stopbits=1,
            timeout=timeout
        )
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        time.sleep(0.1)

    def send_command(self, command):
        try:
            self.ser.write((command + '\n').encode())
            time.sleep(0.3)
            response = self.ser.readline()
            if response:
                decoded = response.decode('ascii', errors='ignore').strip()
                return decoded
            return None
        except Exception as e:
            print(f"Communication error: {e}")
            return None

    def read_sensor(self, input_or_channel):
        """
        Reads voltage, resistance, or other sensor unit as set on lakeshore display
        Input A (3-head) and Input C (4-head) will yield resistance in Ohms
        Channel D5 (4-pump) and D4 (3-pump) will yield voltage in Volts
        Args:
            input_or_channel: 'A', 'B', 'C', 'D1', 'D2', 'D3', 'D4', 'D5'
        Returns:
            float: Sensor units (Ohms or Volts)
            str: "R_OVER" if over-range
            str: "NO_RESPONSE" if no communication
        """
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D1', 'D2', 'D3', 'D4', 'D5']:
            channel_identifier = input_or_channel.upper()
        else:
            channel_identifier = input_or_channel
        response = self.send_command(f"SRDG? {channel_identifier}")
        if response is None or response == "":
            return "NO_RESPONSE"
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "R_OVER"
        try:
            return float(response)
        except ValueError:
            if any(indicator in response.upper() for indicator in ['OVER', 'R.', 'R_']):
                return "R_OVER"
            return response

    def read_temperature(self, input_or_channel):
        """
        Main Temperature Reading Function
        Args:
            input_or_channel: Input or channel label (i.e., 'A', 'B', 'C', 'D2', 'D3', 'D4', 'D5', 1-8)
        Returns:
            float: Temperature in Kelvin (most inputs)
            float: Resistance in Ohms (for A, C)
            float: Voltage in Volts (for D4, D5)
            str: "T_OVER" if temperature is over-range
            str: "NO_RESPONSE" if no communication

        """
         # Special Handling:
            # For 'A', 'C', 'D4', 'D5', returns sensor units (resistance or voltage) instead of temperature.
            # Executes read_sensor() for these inputs instead of read_temperature()
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'C', 'D4', 'D5']:
            return self.read_sensor(input_or_channel)

        channel_identifier = str(input_or_channel)

        # Checking for  over-range status first
        status_response = self.send_command(f"RDGST? {channel_identifier}")
        try:
            if status_response:
                status_code = int(status_response)
                if status_code & 32:
                    return "T_OVER"
        except ValueError:
            pass

        # Reading temperature
        response = self.send_command(f"KRDG? {channel_identifier}")
        if response is None or response == "":
            return "NO_RESPONSE"
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "T_OVER"
        try:
            temp_value = float(response)
            if temp_value == 0.0 and channel_identifier.upper() in ['D2', 'D3', 'D4', 'D5']:
                return "T_OVER"
            return temp_value
        except ValueError:
            if any(indicator in response.upper() for indicator in ['OVER', 'T.', 'T_']):
                return "T_OVER"
            return response

    # Closing serial connection
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
