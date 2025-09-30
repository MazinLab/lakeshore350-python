#!/usr/bin/env python3
"""
Main interface for Lakeshore 350 Driver
"""

import argparse
import serial
from .temperature import TemperatureReader
from .query_heaters import HeaterController

def main():
    parser = argparse.ArgumentParser(description="Lakeshore 350 Temperature Controller")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--input", help="Read specific input (A, B, C, D)")
    parser.add_argument("--channel", type=int, help="Read specific channel (2-5)")
    parser.add_argument("--channels", nargs='+', type=int, help="Read multiple channels (e.g., --channels 2 3 4 5)")
    parser.add_argument("--all-inputs", action="store_true", help="Read all sensor inputs (A, B, C, D)")
    parser.add_argument("--all", action="store_true", help="Read all inputs and channels 2-5")
    parser.add_argument("--info", action="store_true", help="Get device information")
    
    # Heater query arguments (safe - query only)
    parser.add_argument("--query-relay", type=int, choices=[1, 2], help="Query relay heater status (1 for He4 pump, 2 for 3He pump)")
    parser.add_argument("--query-analog", type=int, choices=[3, 4], help="Query analog heater/switch status (3 for 4He pump, 4 for 3He pump)")
    parser.add_argument("--query-all-relays", action="store_true", help="Query both relay heaters (both 3He and 4He pump heaters)")
    parser.add_argument("--query-all-analogs", action="store_true", help="Query both analog heaters/switches (GL7 heat switches)")
    parser.add_argument("--query-all-heaters", action="store_true", help="Query all heaters (relays + analog outputs)")
    
    args = parser.parse_args()
    
    # If no specific action requested, default to reading all inputs
    if not any([args.input, args.channel, args.channels, args.all_inputs, args.all, args.info,
                args.query_relay, args.query_analog, args.query_all_relays, 
                args.query_all_analogs, args.query_all_heaters]):
        args.all_inputs = True
    
    try:
        temp_reader = TemperatureReader(port=args.port)
        heater_controller = HeaterController(temp_reader.send_command)
        
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
        
        # Heater query commands (safe - read only)
        if args.query_relay:
            print(f"Relay Heater {args.query_relay} Status:")
            result = heater_controller.query_relay_heater(args.query_relay)
            print(f"  Raw Config: {result['config_raw']}")
            print(f"  Raw Status: {result['status_raw']}")
            if result['config_parsed']:
                print(f"  Mode: {result['config_parsed']['mode_text']}")
                if 'alarm_text' in result['config_parsed']:
                    print(f"  Alarm Input: {result['config_parsed']['input_alarm']}")
                    print(f"  Alarm Type: {result['config_parsed']['alarm_text']}")
            if result['status_parsed']:
                print(f"  Current Status: {result['status_parsed']['status_text']}")
        
        if args.query_analog:
            print(f"Analog Output {args.query_analog} Status:")
            result = heater_controller.query_analog_heater(args.query_analog)
            print(f"  Raw Config: {result['config_raw']}")
            if result['config_parsed']:
                parsed = result['config_parsed']
                print(f"  Input Channel: {parsed['input_text']}")
                print(f"  Units: {parsed['units_text']}")
                print(f"  Range: {parsed['low_value']} to {parsed['high_value']}")
                print(f"  Output Type: {parsed['polarity_text']}")
        
        if args.query_all_relays:
            print("All Relay Heaters (He4 and He3 Pump Heaters):")
            results = heater_controller.query_all_relay_heaters()
            for name, result in results.items():
                relay_num = result['relay_number']
                print(f"  Relay {relay_num}:")
                print(f"    Config: {result['config_raw']}")
                print(f"    Status: {result['status_raw']}")
                if result['config_parsed']:
                    print(f"    Mode: {result['config_parsed']['mode_text']}")
                if result['status_parsed']:
                    print(f"    State: {result['status_parsed']['status_text']}")
        
        if args.query_all_analogs:
            print("All Analog Outputs (He4 and He3 Pump Heat Switches):")
            results = heater_controller.query_all_analog_heaters()
            for name, result in results.items():
                output_num = result['output_number']
                print(f"  Analog Output {output_num}:")
                print(f"    Config: {result['config_raw']}")
                if result['config_parsed']:
                    parsed = result['config_parsed']
                    print(f"    Input: {parsed['input_text']}")
                    print(f"    Units: {parsed['units_text']}")
                    print(f"    Range: {parsed['low_value']} to {parsed['high_value']}")
        
        if args.query_all_heaters:
            print("All Heater Systems Status:")
            results = heater_controller.query_all_heaters()

            print("\n  Relay Heaters (He4 and He3 Pump Heaters):")
            for name, result in results.items():
                if 'relay_heater' in name:
                    relay_num = result['relay_number']
                    print(f"    Relay {relay_num}: {result['config_raw']} | Status: {result['status_raw']}")
                    
            print("\n  Analog Outputs (He4 and He3 Pump Heat Switches):")
            for name, result in results.items():
                if 'analog_heater' in name:
                    output_num = result['output_number']
                    print(f"    Analog {output_num}: {result['config_raw']}")
    
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
