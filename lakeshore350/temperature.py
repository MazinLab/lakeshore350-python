#!/usr/bin/env python3
"""
Temperature reading functionality for Lake Shore 350
"""

import serial
import time

class TemperatureReader:
    def __init__(self, port="/dev/ttyUSB2", baudrate=57600, timeout=2):
        """Initialize connection to Lake Shore 350"""
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=7,
            parity='O',  # Odd parity
            stopbits=1,
            timeout=timeout
        )
        # Clear any existing data
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        time.sleep(0.1)
    
    def send_command(self, command):
        """Send a command and get response"""
        try:
            self.ser.write((command + '\n').encode())
            time.sleep(0.3)  # Wait for response
            response = self.ser.readline()
            
            if response:
                decoded = response.decode('ascii', errors='ignore').strip()
                return decoded
            return None
        except Exception as e:
            print(f"Communication error: {e}")
            return None
    
    def read_resistance(self, input_or_channel):
        """
        Read resistance from a specific input or channel
        Inputs: A, B, C, D (temperature sensor inputs)
        Returns resistance in ohms for resistance sensors
        """
        # For resistance readings, we use input letters directly
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D']:
            input_letter = input_or_channel.upper()
        else:
            # For numbered inputs, map back to letters
            input_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
            input_letter = input_map.get(input_or_channel, str(input_or_channel))
        
        response = self.send_command(f"SRDG? {input_letter}")
        
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # Handle over-range conditions
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "R_OVER"
        
        # Try to parse as float
        try:
            return float(response)
        except ValueError:
            # Check for over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'R.', 'R_']):
                return "R_OVER"
            return response  # Return as-is if it's some other message

    def read_voltage(self, input_or_channel):
        """
        Read voltage from a specific input or channel
        Inputs: A, B, C, D (temperature sensor inputs)
        Returns voltage in volts
        """
        # For voltage readings, we use input letters directly
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D']:
            input_letter = input_or_channel.upper()
        else:
            # For numbered inputs, map back to letters
            input_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
            input_letter = input_map.get(input_or_channel, str(input_or_channel))
        
        response = self.send_command(f"VRDG? {input_letter}")
        
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # Handle over-range conditions
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "V_OVER"
        
        # Try to parse as float
        try:
            return float(response)
        except ValueError:
            # Check for over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'V.', 'V_']):
                return "V_OVER"
            return response  # Return as-is if it's some other message

    def read_temperature(self, input_or_channel):
        """
        Read temperature from a specific input or channel
        Inputs: A, B, C, D (temperature sensor inputs)
        Channels: 2, 3, 4, 5 (can be used for control loops)
        
        Special handling for GL7:
        - Input A (3-head): Returns resistance in ohms
        - Input C (4-head): Returns resistance in ohms
        - All others: Returns temperature in Kelvin
        """
        # Special GL7 handling: read resistance for 3-head and 4-head
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'C']:
            return self.read_resistance(input_or_channel)
        
        # Regular temperature reading for all other inputs/channels
        # Map letter inputs to numbers for KRDG command
        input_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        
        if isinstance(input_or_channel, str) and input_or_channel.upper() in input_map:
            channel_num = input_map[input_or_channel.upper()]
        else:
            channel_num = input_or_channel
        
        response = self.send_command(f"KRDG? {channel_num}")
        
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # Handle over-range conditions
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "T_OVER"
        
        # Try to parse as float
        try:
            return float(response)
        except ValueError:
            # Check for over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'T.', 'T_']):
                return "T_OVER"
            return response  # Return as-is if it's some other message
    
    def read_all_inputs(self):
        """Read temperatures from all sensor inputs (A, B, C, D)"""
        inputs = ['A', 'B', 'C', 'D']
        results = {}
        
        for input_name in inputs:
            temp = self.read_temperature(input_name)
            results[f"Input_{input_name}"] = temp
            time.sleep(0.1)  # Small delay between readings
        
        return results
    
    def read_channels(self, channel_list):
        """Read temperatures from specific channels"""
        results = {}
        
        for channel in channel_list:
            temp = self.read_temperature(channel)
            results[f"Channel_{channel}"] = temp
            time.sleep(0.1)  # Small delay between readings
        
        return results
    
    def get_device_info(self):
        """Get device identification"""
        return self.send_command("*IDN?")
    
    def close(self):
        """Close the serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
