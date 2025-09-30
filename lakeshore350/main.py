#!/usr/bin/env python3
"""
Main interface for Lakeshore 350 Driver
"""

import argparse
import serial
from .temperature import TemperatureReader

def main():
    parser = argparse.ArgumentParser(description="Lakeshore 350 Temperature Controller")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--input", help="Read specific input (A, B, C, D)")
    parser.add_argument("--channel", type=int, help="Read specific channel (2-5)")
    parser.add_argument("--channels", nargs='+', type=int, help="Read multiple channels (e.g., --channels 2 3 4 5)")
    parser.add_argument("--all-inputs", action="store_true", help="Read all sensor inputs (A, B, C, D)")
    parser.add_argument("--all", action="store_true", help="Read all inputs and channels 2-5")
    parser.add_argument("--info", action="store_true", help="Get device information")
    
    args = parser.parse_args()
    
    # If no specific action requested, default to reading all inputs
    if not any([args.input, args.channel, args.channels, args.all_inputs, args.all, args.info]):
        args.all_inputs = True
    
    try:
        temp_reader = TemperatureReader(port=args.port)
        
        if args.info:
            print("Device Information:")
            info = temp_reader.get_device_info()
            print(f"  {info if info else 'No response'}")
            print()
        
        if args.input:
            print(f"Input {args.input.upper()} Temperature:")
            temp = temp_reader.read_temperature(args.input)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channel:
            print(f"Channel {args.channel} Temperature:")
            temp = temp_reader.read_temperature(args.channel)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channels:
            print("Selected Channels:")
            temps = temp_reader.read_channels(args.channels)
            for channel_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
        
        if args.all_inputs:
            print("All Sensor Inputs:")
            temps = temp_reader.read_all_inputs()
            for input_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
        
        if args.all:
            print("All Inputs (A-D):")
            input_temps = temp_reader.read_all_inputs()
            for input_name, temp in input_temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
            
            print("\nAll Channels (1-8):")
            channel_temps = temp_reader.read_channels([1, 2, 3, 4, 5, 6, 7, 8])
            for channel_name, temp in channel_temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
    
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print("Make sure the Lakeshore 350 is connected and the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            temp_reader.close()
        except:
            pass

if __name__ == "__main__":
    main()
