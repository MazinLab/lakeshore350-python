#!/usr/bin/env python3
"""
GL7 Heat Switch Control Script
Control individual heat switches and query their status.
"""

import argparse
import sys
import time

# Handle imports for both direct execution and module import
try:
    from .gl7_control import GL7Controller
    from .temperature import TemperatureReader
except ImportError:
    # Direct execution path
    from gl7_control import GL7Controller
    from temperature import TemperatureReader

def set_switch_state(gl7_controller, switch_num, state):
    """Set heat switch to ON (5V) or OFF (0V)"""
    switch_name = "4-switch" if switch_num == 3 else "3-switch"
    analog_output = switch_num  # 3 for 4-switch, 4 for 3-switch
    
    print(f"Setting {switch_name} to {state}")
    
    try:
        if state.upper() == "ON":
            # Turn ON: Set to 5V using full ANALOG command
            gl7_controller.send_command(f"ANALOG {analog_output},1,1,5.0,0.0,0")
        elif state.upper() == "OFF":
            # Turn OFF: Set to 0V using simplified ANALOG command
            gl7_controller.send_command(f"ANALOG {analog_output},0")
        else:
            print(f"  Error: Invalid state '{state}'. Use 'ON' or 'OFF'")
            return False
        
        return True
    except Exception as e:
        print(f"  Error setting {switch_name}: {e}")
        return False

def query_switch_status(gl7_controller, switch_num):
    """Query and display heat switch status"""
    try:
        switch_name = "4-switch" if switch_num == 3 else "3-switch"
        analog_output = switch_num  # 3 for 4-switch, 4 for 3-switch
        
        config = gl7_controller.query_analog_status(analog_output)
        
        # Parse the config to determine ON/OFF status and voltage
        status_text = "UNKNOWN"
        try:
            if config:
                config_parts = config.split(',')
                if len(config_parts) >= 3:
                    status_value = int(config_parts[0])
                    voltage = float(config_parts[2])
                    
                    if status_value == 1:
                        status_text = f"ON ({voltage:.1f}V)"
                    else:
                        status_text = f"OFF ({voltage:.1f}V)"
                else:
                    status_text = f"RAW: {config}"
        except (ValueError, IndexError) as e:
            status_text = f"PARSE_ERROR: {config}"
        
        print(f"  {switch_name} (Analog Output {analog_output}): {status_text}")
        
        return config, status_text
    except Exception as e:
        print(f"  Error querying {switch_name}: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='GL7 Heat Switch Control')
    parser.add_argument('switch', type=int, nargs='?', choices=[3, 4],
                       help='Switch number (3 for 4-switch, 4 for 3-switch)')
    parser.add_argument('state', type=str, nargs='?', choices=['ON', 'OFF', 'on', 'off'],
                       help='Switch state (ON or OFF)')
    parser.add_argument('--both', type=str, choices=['ON', 'OFF', 'on', 'off'],
                       help='Set both switches to same state: --both ON/OFF')
    parser.add_argument('--query', action='store_true',
                       help='Query current switch status without changing settings')
    parser.add_argument('--port', type=str, default='/dev/ttyUSB0',
                       help='Serial port for Lakeshore 350 (default: /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=57600,
                       help='Baud rate for serial communication (default: 57600)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.query and not args.both and (args.switch is None or args.state is None):
        parser.error("Must specify either 'switch state', '--both ON/OFF', or '--query'")
    
    print("Initializing GL7 Heat Switch Control...")
    print(f"Connecting to Lakeshore 350 on {args.port}...")
    
    try:
        # Initialize temperature reader and GL7 controller
        temp_reader = TemperatureReader(port=args.port)
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        if args.query:
            # Query mode - just show current status
            print("\nCurrent Heat Switch Status:")
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
            
        elif args.both:
            # Set both switches
            state = args.both.upper()
            set_switch_state(gl7_controller, 3, state)  # 4-switch
            set_switch_state(gl7_controller, 4, state)  # 3-switch
            
            # Wait a moment for commands to take effect
            time.sleep(1)
            
            # Show status of both switches
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
                
        else:
            # Set single switch
            state = args.state.upper()
            set_switch_state(gl7_controller, args.switch, state)
            
            # Wait a moment for commands to take effect
            time.sleep(1)
            
            # Show status of both switches
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
        
        # Close connection
        temp_reader.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR during switch control: {e}")
        print("Manual intervention may be required!")
        sys.exit(1)

if __name__ == "__main__":
    main()
