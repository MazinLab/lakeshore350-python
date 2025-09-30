#!/usr/bin/env python3
"""
Simple Lake Shore 350 Temperature Controller Interface
Reads temperature from all channels or specific channels
"""

import serial
import time
import argparse

class LakeShore350:
    def __init__(self, port="/dev/ttyUSB0", baudrate=57600, timeout=2):
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
    
    def read_temperature(self, input_or_channel):
        """
        Read temperature from a specific input or channel
        Inputs: A, B, C, D (temperature sensor inputs)
        Channels: 2, 3, 4, 5 
        """
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

def main():
    parser = argparse.ArgumentParser(description="Lake Shore 350 Temperature Reader")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--input", help="Read specific input (A, B, C, D)")
    parser.add_argument("--channel", type=int, help="Read specific channel (1-8)")
    parser.add_argument("--channels", nargs='+', type=int, help="Read multiple channels (e.g., --channels 2 3 4 5)")
    parser.add_argument("--all-inputs", action="store_true", help="Read all sensor inputs (A, B, C, D)")
    parser.add_argument("--all", action="store_true", help="Read all inputs and channels 1-8")
    parser.add_argument("--info", action="store_true", help="Get device information")
    
    args = parser.parse_args()
    
    # If no specific action requested, default to reading all inputs
    if not any([args.input, args.channel, args.channels, args.all_inputs, args.all, args.info]):
        args.all_inputs = True
    
    try:
        ls = LakeShore350(port=args.port)
        
        if args.info:
            print("Device Information:")
            info = ls.get_device_info()
            print(f"  {info if info else 'No response'}")
            print()
        
        if args.input:
            print(f"Input {args.input.upper()} Temperature:")
            temp = ls.read_temperature(args.input)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channel:
            print(f"Channel {args.channel} Temperature:")
            temp = ls.read_temperature(args.channel)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channels:
            print("Selected Channels:")
            temps = ls.read_channels(args.channels)
            for channel_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
        
        if args.all_inputs:
            print("All Sensor Inputs:")
            temps = ls.read_all_inputs()
            for input_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
        
        if args.all:
            print("All Inputs (A-D):")
            input_temps = ls.read_all_inputs()
            for input_name, temp in input_temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
            
            print("\nAll Channels (1-8):")
            channel_temps = ls.read_channels([1, 2, 3, 4, 5, 6, 7, 8])
            for channel_name, temp in channel_temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
    
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print("Make sure the Lake Shore 350 is connected and the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            ls.close()
        except:
            pass

if __name__ == "__main__":
    main()
