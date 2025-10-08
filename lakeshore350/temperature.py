#!/usr/bin/env python3
"""
Temperature reading functionality for Lake Shore 350

This module provides centralized temperature reading for all Lakeshore 350 operations.
All temperature/resistance/voltage serial commands are handled here.

Key Functions:
- read_temperature(): Main function - returns temp in K or resistance in Ω
- read_resistance(): Direct resistance reading in Ω  
- read_voltage(): Direct voltage reading in V
- send_command(): Low-level serial communication

Hardware Mapping:
- Regular Inputs: A, B, C, D (physical inputs on device)
- Special Inputs: D2, D3, D4, D5 (internal channels)
- Channels: 1-8 (control loop channels)
"""

import serial
import time

class TemperatureReader:
    """
    Centralized temperature reading for Lakeshore 350
    
    This class handles ALL temperature/resistance/voltage readings for the entire project.
    Other modules should use this class instead of sending serial commands directly.
    
    Usage Examples:
        temp_reader = TemperatureReader()
        
        # Temperature readings (returns float in Kelvin or "T_OVER")
        temp = temp_reader.read_temperature(5)      # Channel 5 (4-pump)
        temp = temp_reader.read_temperature(2)      # Channel 2 (50K stage)
        temp = temp_reader.read_temperature('D3')   # Special input D3 (4K stage)
        temp = temp_reader.read_temperature('B')    # Regular input B (device stage)
        
        # Resistance readings (returns float in Ohms or "R_OVER") 
        resistance = temp_reader.read_resistance('A')  # Input A (3-head)
        
    Serial Commands Used:
        KRDG? - Kelvin temperature reading
        SRDG? - Resistance reading  
        VRDG? - Voltage reading
        RDGST? - Status reading (detects over-range conditions)
    """
    
    def __init__(self, port="/dev/ttyUSB2", baudrate=57600, timeout=2):
        """
        Initialize connection to Lake Shore 350
        
        Serial Settings (DO NOT CHANGE unless hardware changes):
        - Port: /dev/ttyUSB2 (default USB connection)
        - Baudrate: 57600 (Lakeshore 350 default)
        - Bytesize: 7 bits
        - Parity: Odd ('O') 
        - Stopbits: 1
        - Timeout: 2 seconds
        """
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
        """
        LOW-LEVEL SERIAL COMMUNICATION - Handle with care!
        
        Sends a raw command to the Lakeshore 350 and returns the response.
        This is the foundation that all other methods build on.
        
        Args:
            command (str): Raw Lakeshore command (e.g., "KRDG? 5", "SRDG? A")
            
        Returns:
            str: Raw response from device, or None if communication fails
            
        Timing Critical:
        - 0.3 second delay after sending (DO NOT REDUCE - device needs time)
        - Longer delays are safe but slow down readings
        
        Error Handling:
        - Returns None if communication fails
        - Strips whitespace from response
        - Handles ASCII decoding errors gracefully
        """
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
        RESISTANCE READING - Uses SRDG? command
        
        Reads resistance in Ohms from temperature sensors.
        Primarily used for 3-head (Input A) and 4-head (Input C) sensors.
        
        Args:
            input_or_channel: 'A', 'B', 'C', 'D' or channel number
            
        Returns:
            float: Resistance in Ohms (e.g., 1019.35)
            str: "R_OVER" if resistance is over-range
            str: "NO_RESPONSE" if no communication
            
        Over-Range Detection:
        - Response length > 15 characters
        - Contains backtick (`) or null bytes
        - Contains "OVER", "R.", or "R_" text
        """
        # Use input letters directly for SRDG command
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D']:
            channel_identifier = input_or_channel.upper()
        else:
            channel_identifier = input_or_channel
        
        # CORE SERIAL COMMAND: Send SRDG? (Sensor Resistance Query)
        response = self.send_command(f"SRDG? {channel_identifier}")
        
        # Handle communication failures
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # OVER-RANGE DETECTION: Multiple methods to catch bad readings
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "R_OVER"
        
        # Try to convert to float (normal case)
        try:
            return float(response)
        except ValueError:
            # Check for text-based over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'R.', 'R_']):
                return "R_OVER"
            return response  # Return raw response for debugging

    def read_voltage(self, input_or_channel):
        """
        VOLTAGE READING - Uses VRDG? command
        
        Reads voltage in Volts from temperature sensors.
        Functionality not current implemented but may use in the future 
        
        Args:
            input_or_channel: 'A', 'B', 'C', 'D' or channel number
            
        Returns:
            float: Voltage in Volts
            str: "V_OVER" if voltage is over-range
            str: "NO_RESPONSE" if no communication
        """
        # Use input letters directly for VRDG command
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D']:
            channel_identifier = input_or_channel.upper()
        else:
            channel_identifier = input_or_channel
        
        # CORE SERIAL COMMAND: Send VRDG? (Voltage Reading Query)
        response = self.send_command(f"VRDG? {channel_identifier}")
        
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # Handle over-range conditions (same logic as resistance)
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "V_OVER"
        
        # Try to convert to float
        try:
            return float(response)
        except ValueError:
            # Check for voltage-specific over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'V.', 'V_']):
                return "V_OVER"
            return response  # Return raw response for debugging

    def read_temperature(self, input_or_channel):
        """
        MAIN TEMPERATURE READING FUNCTION - Uses KRDG? command
        
        This is the PRIMARY function used throughout the project.
        Returns temperature in Kelvin OR resistance in Ohms (for GL7 heads).
        
        Args:
            input_or_channel: Various formats accepted:
                - 'A', 'B', 'C', 'D' (regular inputs)
                - 'D2', 'D3', 'D4', 'D5' (special inputs)  
                - 1, 2, 3, 4, 5, 6, 7, 8 (channels)
                
        Returns:
            float: Temperature in Kelvin (e.g., 161.23) 
            float: Resistance in Ohms (for inputs A, C only)
            str: "T_OVER" if temperature is over-range
            str: "NO_RESPONSE" if no communication
            
        SPECIAL GL7 BEHAVIOR:
        - Input A (3-head): Returns RESISTANCE in Ohms (not temperature)
        - Input C (4-head): Returns RESISTANCE in Ohms (not temperature)  
        - All others: Return temperature in Kelvin
        
        Hardware Mapping:
            Regular Inputs:
                'A' → Input A (3-head resistance) → Returns Ω
                'B' → Input B (1K GGG temperature) → Returns K  
                'C' → Input C (4-head resistance) → Returns Ω
                'D' → Input D (3-pump temperature) → Returns K
                
            Special Inputs:
                'D2' → 4K stage diode → Returns K
                'D3' → 60K stage diode → Returns K
                'D4' → GL7 Film Burner → Returns K
                'D5' → Unused → Returns K
                
            Channels:
                1-8 → Control loop channels → Returns K
                5 → 4-pump temperature (most common) → Returns K
        
        Status Checking:
        - Uses RDGST? command first to detect over-range
        - Bit 5 (value 32) in status indicates T_OVER
        - Double-checks 0.0 readings as potentially over-range
        """
        # ===== SPECIAL GL7 HANDLING =====
        # For 3-head (A) and 4-head (C): Return resistance instead of temperature
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'C']:
            return self.read_resistance(input_or_channel)
        
        # ===== INPUT/CHANNEL MAPPING =====
        # Convert various input formats to the channel identifier used in serial commands
        if isinstance(input_or_channel, str) and input_or_channel.upper() in ['A', 'B', 'C', 'D']:
            # CRITICAL MAPPING: Input D is actually channel 4 (3-pump)
            if input_or_channel.upper() == 'D':
                channel_identifier = '4'  # 3-pump is on channel 4, not input D
            else:
                channel_identifier = input_or_channel.upper()
        else:
            # For numeric channels (1-8) or special inputs (D2-D5)
            channel_identifier = str(input_or_channel)
        
        # ===== STATUS CHECK FIRST =====
        # Use RDGST? to detect over-range conditions before reading temperature
        status_response = self.send_command(f"RDGST? {channel_identifier}")
        try:
            if status_response:
                status_code = int(status_response)
                # CRITICAL: Bit 5 (value 32) indicates temperature over-range
                if status_code & 32:  # Binary AND to check bit 5
                    return "T_OVER"
        except ValueError:
            # If status reading fails, continue to temperature reading
            pass
        
        # ===== MAIN TEMPERATURE READING =====
        # CORE SERIAL COMMAND: Send KRDG? (Kelvin Reading Query)
        response = self.send_command(f"KRDG? {channel_identifier}")
        
        if response is None or response == "":
            return "NO_RESPONSE"
        
        # Handle over-range conditions in the response itself
        if len(response) > 15 or '`' in response or '\x00' in response:
            return "T_OVER"
        
        # ===== TEMPERATURE VALUE PROCESSING =====
        try:
            temp_value = float(response)
            
            # SAFETY CHECK: 0.0 readings are suspicious for certain inputs
            # Special inputs D2-D5 that read 0.0 are likely over-range
            if temp_value == 0.0 and channel_identifier.upper() in ['D2', 'D3', 'D4', 'D5']:
                return "T_OVER"
                
            return temp_value
        except ValueError:
            # Check for text-based over-range indicators
            if any(indicator in response.upper() for indicator in ['OVER', 'T.', 'T_']):
                return "T_OVER"
            return response  # Return raw response for debugging
    
    def read_all_inputs(self):
        """
        CONVENIENCE FUNCTION: Read all regular inputs (A-D)
        
        Returns a dictionary with all input readings.
        Useful for getting a complete snapshot of the system.
        """
        inputs = ['A', 'B', 'C', 'D']
        results = {}
        
        for input_name in inputs:
            temp = self.read_temperature(input_name)
            results[f"Input_{input_name}"] = temp
            time.sleep(0.1)  # Small delay between readings to avoid overwhelming device
        
        return results
    
    def read_channels(self, channel_list):
        """
        CONVENIENCE FUNCTION: Read specific channels
        
        Args:
            channel_list: List of channel numbers [1, 2, 3, 5] 
            
        Returns:
            dict: {'Channel_1': temp, 'Channel_2': temp, ...}
        """
        results = {}
        
        for channel in channel_list:
            temp = self.read_temperature(channel)
            results[f"Channel_{channel}"] = temp
            time.sleep(0.1)  # Small delay between readings
        
        return results
    
    def get_device_info(self):
        """
        UTILITY FUNCTION: Get device identification
        
        Returns device model, firmware version, etc.
        Useful for troubleshooting and verification.
        """
        return self.send_command("*IDN?")
    
    def close(self):
        """
        CLEANUP FUNCTION: Close the serial connection
        
        Always call this when done to free up the serial port.
        Python garbage collection should handle this automatically,
        but explicit cleanup is good practice.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
