#!/usr/bin/env python3
"""
GL7 Heater Control Script
Control individual heater outputs and query their status.
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

def set_heater_output(gl7_controller, output_num, power_percent):
    """Set heater output to specified power percentage"""
    print(f"Setting Heater Output {output_num} to {power_percent}%...")
    
    try:
        # Set heater to manual mode (Mode 3) and specified power
        gl7_controller.send_command(f"OUTMODE {output_num},3,0,0")
        gl7_controller.send_command(f"MOUT {output_num},{power_percent}")
        print(f"  Heater Output {output_num}: SET to {power_percent}% power")
        return True
    except Exception as e:
        print(f"  Error setting heater output {output_num}: {e}")
        return False

def query_heater_status(gl7_controller, output_num):
    """Query and display heater status"""
    try:
        mode, output = gl7_controller.query_heater_output_status(output_num)
        
        try:
            output_val = float(output) if output and output != "NO_RESPONSE" else output
        except (ValueError, TypeError):
            output_val = output
        
        heater_name = "4-pump Heater" if output_num == 1 else "3-pump Heater"
        print(f"  {heater_name} (Output {output_num}): Mode={mode}, Power={output_val}%")
        
        return mode, output_val
    except Exception as e:
        print(f"  Error querying heater output {output_num}: {e}")
        return None, None

def emergency_stop_heaters(gl7_controller):
    """Emergency stop - shut down all heaters immediately"""
    print("EMERGENCY HEATER STOP INITIATED")
    print("=" * 50)
    print("Shutting down all heaters...")
    
    # Turn off all heater outputs (1 & 2)
    print("\nShutting down heater outputs:")
    success_list = []
    
    try:
        # Turn off 4-pump heater (Output 1)
        gl7_controller.send_command("MOUT 1,0.0")
        print("  4-pump Heater (Output 1): SHUT DOWN (0% power)")
        success_list.append(True)
    except Exception as e:
        print(f"  Error shutting down 4-pump heater: {e}")
        success_list.append(False)
    
    try:
        # Turn off 3-pump heater (Output 2)
        gl7_controller.send_command("MOUT 2,0.0")
        print("  3-pump Heater (Output 2): SHUT DOWN (0% power)")
        success_list.append(True)
    except Exception as e:
        print(f"  Error shutting down 3-pump heater: {e}")
        success_list.append(False)
    
    # Wait a moment for commands to take effect
    time.sleep(2)
    
    # Status confirmation
    print("\nPOST-SHUTDOWN STATUS CONFIRMATION")
    print("=" * 50)
    
    # Check all temperatures
    print("\nTemperature Readings:")
    try:
        # Head temperatures
        temp_3he_head = gl7_controller.read_temperature('A')
        temp_4he_head = gl7_controller.read_temperature('C')
        temp_device = gl7_controller.read_temperature('B')
        temp_3pump = gl7_controller.read_temperature('D')
        
        # Stage temperatures
        temp_channel_2 = gl7_controller.send_command("KRDG? 2")
        temp_channel_3 = gl7_controller.send_command("KRDG? 3")
        temp_channel_5 = gl7_controller.send_command("KRDG? 5")
        
        try:
            temp_4k_val = float(temp_channel_2) if temp_channel_2 and temp_channel_2 != "T_OVER" else temp_channel_2
        except ValueError:
            temp_4k_val = temp_channel_2
            
        try:
            temp_50k_val = float(temp_channel_3) if temp_channel_3 and temp_channel_3 != "T_OVER" else temp_channel_3
        except ValueError:
            temp_50k_val = temp_channel_3
            
        try:
            temp_4pump_val = float(temp_channel_5) if temp_channel_5 and temp_channel_5 != "T_OVER" else temp_channel_5
        except ValueError:
            temp_4pump_val = temp_channel_5
        
        print(f"  3-head (Input A): {temp_3he_head} K")
        print(f"  4-head (Input C): {temp_4he_head} K")
        print(f"  3-pump (Input D): {temp_3pump} K")
        print(f"  4-pump (Channel 5): {temp_4pump_val} K")
        print(f"  50K Stage (Channel 3): {temp_50k_val} K")
        print(f"  4K Stage (Channel 2): {temp_4k_val} K")
        print(f"  Device Stage (Input B): {temp_device} K")
        
    except Exception as e:
        print(f"  Error reading temperatures: {e}")
    
    # Check heater status
    print("\nHeater Status Confirmation:")
    query_heater_status(gl7_controller, 1)
    query_heater_status(gl7_controller, 2)
    
    print("\nHeaters shut off")
    
    return all(success_list)

def main():
    """Main heater control function"""
    parser = argparse.ArgumentParser(description='GL7 Heater Control - Set heater outputs to specified power levels')
    parser.add_argument('output', type=int, choices=[1, 2], nargs='?',
                       help='Heater output number (1 for 4-pump, 2 for 3-pump)')
    parser.add_argument('power', type=float, nargs='?',
                       help='Power percentage (0-100)')
    parser.add_argument('--both', nargs=2, type=float, metavar=('POWER1', 'POWER2'),
                       help='Set both heaters: --both <power1> <power2>')
    parser.add_argument('--query', action='store_true',
                       help='Query current heater status without changing settings')
    parser.add_argument('--stop', action='store_true',
                       help='Emergency stop: immediately shut down both heaters')
    parser.add_argument('--port', type=str, default='/dev/ttyUSB2',
                       help='Serial port for Lakeshore 350 (default: /dev/ttyUSB2)')
    parser.add_argument('--baudrate', type=int, default=57600,
                       help='Baud rate for serial communication (default: 57600)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.query and not args.both and not args.stop and (args.output is None or args.power is None):
        parser.error("Must specify either 'output power', '--both power1 power2', '--query', or '--stop'")
    
    if args.power is not None and (args.power < 0 or args.power > 100):
        parser.error("Power must be between 0 and 100")
    
    if args.both and (any(p < 0 or p > 100 for p in args.both)):
        parser.error("Both power values must be between 0 and 100")
    
    print("Initializing GL7 Heater Control...")
    print(f"Connecting to Lakeshore 350 on {args.port}...")
    
    try:
        # Initialize temperature reader and GL7 controller
        temp_reader = TemperatureReader(port=args.port)
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        if args.query:
            # Query mode - just show current status
            print("\nCurrent Heater Status:")
            query_heater_status(gl7_controller, 1)
            query_heater_status(gl7_controller, 2)
            
        elif args.stop:
            # Emergency stop mode
            success = emergency_stop_heaters(gl7_controller)
            if success:
                print("\nEmergency heater stop completed successfully.")
            else:
                print("\nWarning: Some heaters may not have been shut down correctly.")
            
        elif args.both:
            # Set both heaters
            print("\nSetting Both Heaters:")
            success1 = set_heater_output(gl7_controller, 1, args.both[0])
            success2 = set_heater_output(gl7_controller, 2, args.both[1])
            
            # Wait a moment for commands to take effect
            time.sleep(1)
            
            # Query status after setting
            print("\nHeater Status After Setting:")
            query_heater_status(gl7_controller, 1)
            query_heater_status(gl7_controller, 2)
            
            if success1 and success2:
                print("\nBoth heaters set successfully.")
            else:
                print("\nWarning: One or more heaters may not have been set correctly.")
                
        else:
            # Set single heater
            heater_name = "4-pump Heater" if args.output == 1 else "3-pump Heater"
            print(f"\nSetting {heater_name}:")
            success = set_heater_output(gl7_controller, args.output, args.power)
            
            # Wait a moment for commands to take effect
            time.sleep(1)
            
            # Query status after setting
            print(f"\n{heater_name} Status After Setting:")
            query_heater_status(gl7_controller, args.output)
            
            if success:
                print(f"\n{heater_name} set successfully.")
            else:
                print(f"\nWarning: {heater_name} may not have been set correctly.")
        
        # Close connection
        temp_reader.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR during heater control: {e}")
        print("Manual intervention may be required!")
        sys.exit(1)

if __name__ == "__main__":
    main()
