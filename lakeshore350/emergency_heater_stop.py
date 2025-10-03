#!/usr/bin/env python3
"""
GL7 Emergency Heater Stop Script
Safely shuts down all heaters, then provides status confirmation.
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

def emergency_shutdown(gl7_controller):
    """Emergency shutdown of all heaters"""
    print("EMERGENCY HEATER STOP INITIATED")
    print("=" * 50)
    print("Shutting down all heaters!")
    
    # Turn off all heater outputs (1 & 2)
    try:
        # Turn off 4-pump heater (Output 1)
        gl7_controller.send_command("MOUT 1,0.0")
        print("  4-pump Heater (Output 1): SHUT DOWN (0% power)")
    except Exception as e:
        print(f"  Error shutting down 4-pump heater: {e}")
    
    try:
        # Turn off 3-pump heater (Output 2)
        gl7_controller.send_command("MOUT 2,0.0")
        print("  3-pump Heater (Output 2): SHUT DOWN (0% power)")
    except Exception as e:
        print(f"  Error shutting down 3-pump heater: {e}")
    
    # Wait a moment for commands to take effect
    time.sleep(2)

def status_confirmation(gl7_controller):
    """Provide comprehensive status confirmation after emergency stop"""
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
        
        print(f"  3He Head (Input A): {temp_3he_head} K")
        print(f"  4He Head (Input C): {temp_4he_head} K")
        print(f"  Device Stage (Input B): {temp_device} K")
        print(f"  3-pump (Input D): {temp_3pump} K")
        
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
        
        print(f"  4K Stage (Channel 2): {temp_4k_val} K")
        print(f"  50K Stage (Channel 3): {temp_50k_val} K")
        print(f"  4-pump (Channel 5): {temp_4pump_val} K")
        
    except Exception as e:
        print(f"  Error reading temperatures: {e}")
    
    # Check heater status
    print("\nHeater Status Confirmation:")
    try:
        mode_1, output_1 = gl7_controller.query_heater_output_status(1)
        mode_2, output_2 = gl7_controller.query_heater_output_status(2)
        
        try:
            output_1_val = float(output_1) if output_1 and output_1 != "NO_RESPONSE" else output_1
        except (ValueError, TypeError):
            output_1_val = output_1
            
        try:
            output_2_val = float(output_2) if output_2 and output_2 != "NO_RESPONSE" else output_2
        except (ValueError, TypeError):
            output_2_val = output_2
        
        print(f"  4-pump Heater (Output 1): Mode={mode_1}, Power={output_1_val}%")
        print(f"  3-pump Heater (Output 2): Mode={mode_2}, Power={output_2_val}%")
        
        # Verify shutdown
        if isinstance(output_1_val, (int, float)) and output_1_val == 0.0:
            print("    4-pump heater confirmed OFF")
        else:
            print("    4-pump heater status unclear")
            
        if isinstance(output_2_val, (int, float)) and output_2_val == 0.0:
            print("    3-pump heater confirmed OFF")
        else:
            print("    3-pump heater status unclear")
            
    except Exception as e:
        print(f"  Error checking heater status: {e}")
    
    print("\nHeaters shut off")

def main():
    """Main emergency heater stop function"""
    parser = argparse.ArgumentParser(description='GL7 Emergency Heater Stop - Shutdown all heaters')
    parser.add_argument('action', nargs='?', default='emergency-heater-stop',
                       help='Action to perform (default: emergency-heater-stop)')
    parser.add_argument('--port', type=str, default='/dev/ttyUSB2',
                       help='Serial port for Lakeshore 350 (default: /dev/ttyUSB2)')
    parser.add_argument('--baudrate', type=int, default=57600,
                       help='Baud rate for serial communication (default: 57600)')
    
    args = parser.parse_args()
    
    if args.action != 'emergency-heater-stop':
        print(f"Unknown action: {args.action}")
        print("Usage: python -m lakeshore350.emergency_heater_stop emergency-heater-stop")
        sys.exit(1)
    
    print("Initializing GL7 Emergency Heater Stop...")
    print(f"Connecting to Lakeshore 350 on {args.port}...")
    
    try:
        # Initialize temperature reader and GL7 controller
        temp_reader = TemperatureReader(port=args.port)
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        # Perform emergency shutdown
        emergency_shutdown(gl7_controller)
        
        # Provide status confirmation
        status_confirmation(gl7_controller)
        
        # Close connection
        temp_reader.close()
        
        print("\nEmergency heater stop completed successfully.")
        print("Connection closed.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR during emergency heater stop: {e}")
        print("Manual intervention may be required!")
        sys.exit(1)

if __name__ == "__main__":
    main()
