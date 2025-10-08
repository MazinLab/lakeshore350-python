#!/usr/bin/env python3
"""
GL7 Heater Control Script - CENTRALIZED HEATER CONTROL
========================================================

This module provides centralized control for all heater operations in the GL7 system.
ALL heater-related serial commands (OUTMODE, MOUT) should go through this module
to maintain single point of control and avoid scattered commands throughout the codebase.

Architecture Design:
- HeaterController class contains all heater serial communication
- GL7 steps import this module and use HeaterController methods
- No direct OUTMODE/MOUT commands in GL7 step files
- Consistent error handling and logging across all heater operations
"""

import argparse
import sys
import time

# IMPORT HANDLING: Support both module import and direct execution
try:
    # When imported as a module (from lakeshore350.heaters import HeaterController)
    from .gl7_control import GL7Controller
    from .temperature import TemperatureReader
except ImportError:
    # When executed directly (python heaters.py)
    from gl7_control import GL7Controller
    from temperature import TemperatureReader

class HeaterController:
    """
    CENTRALIZED HEATER CONTROLLER CLASS
    ===================================
    
    This class is the SINGLE POINT OF CONTROL for all heater operations.
    All GL7 steps should use this class instead of sending OUTMODE/MOUT commands directly.
    
    Hardware Configuration:
    - Output 1: 4-pump heater (4He sorption pump)
    - Output 2: 3-pump heater (3He sorption pump)
    - Mode 3: Open Loop (manual power control, no temperature feedback)
    - Built-in Lakeshore 350 power supplies (up to 1W each)
    """
    
    def __init__(self, gl7_controller):
        """Initialize heater controller with GL7 communication interface"""
        self.gl7_controller = gl7_controller
        
    def set_heater_mode_and_power(self, output_num, power_percent, mode=3):
        """
        SET HEATER MODE AND POWER LEVEL
        ===============================
        
        This is the PRIMARY method for setting heater power in GL7 operations.
        Sends two serial commands in sequence:
        1. OUTMODE: Sets the heater control mode
        2. MOUT: Sets the power percentage
        
        Args:
            output_num (int): Heater output number
                             1 = 4-pump heater (4He sorption pump)
                             2 = 3-pump heater (3He sorption pump)
            power_percent (float): Power level 0-100%
                                  Percentage of maximum 1W output
            mode (int): Heater control mode (default=3)
                       3 = Open Loop (manual control, no temp feedback)
                       
        Serial Commands Sent:
            OUTMODE <output>,<mode>,<input>,<powerup_enable>
            - mode=3: Open Loop (manual)
            - input=0: No sensor input (manual mode)
            - powerup_enable=0: Turn off after power cycle (safety)
            
            MOUT <output>,<power_percent>
            - Sets the actual power percentage (0-100%)
            
        Returns:
            bool: True if both commands successful, False if any errors
        """
        # Determine heater name for user feedback
        heater_name = "4-pump Heater" if output_num == 1 else "3-pump Heater"
        print(f"Setting {heater_name} (Output {output_num}) to {power_percent}% power...")
        
        try:
            # STEP 1: Set heater mode first (OUTMODE command)
            # Format: OUTMODE <output>,<mode>,<input>,<powerup_enable>
            # Example: OUTMODE 1,3,0,0 = Output 1, Open Loop, No Input, Power-off on restart
            self.gl7_controller.send_command(f"OUTMODE {output_num},{mode},0,0")
            
            # STEP 2: Set power level (MOUT command)
            # Format: MOUT <output>,<power_percent>
            # Example: MOUT 1,75 = Output 1 to 75% power
            self.gl7_controller.send_command(f"MOUT {output_num},{power_percent}")
            
            # Success feedback
            print(f"  {heater_name}: SET to {power_percent}% power (Mode {mode})")
            return True
            
        except Exception as e:
            # Error handling with detailed feedback
            print(f"  Error setting {heater_name}: {e}")
            return False
    
    def turn_off_heater(self, output_num):
        """
        TURN OFF SINGLE HEATER (Safety Method)
        ======================================
        
        Sets specified heater to 0% power while maintaining the current mode.
        Used for individual heater shutdown during GL7 operations.
        
        Args:
            output_num (int): Heater output number
                             1 = 4-pump heater
                             2 = 3-pump heater
                             
        Serial Command Sent:
            MOUT <output>,0.0
            - Sets power to 0% (heater off)
            - Mode remains unchanged (still in Mode 3)
            
        Returns:
            bool: True if successful, False if error
        """
        heater_name = "4-pump Heater" if output_num == 1 else "3-pump Heater"
        print(f"Turning OFF {heater_name} (Output {output_num})...")
        
        try:
            # Send MOUT command to set power to 0%
            # This turns off the heater but keeps it in current mode
            self.gl7_controller.send_command(f"MOUT {output_num},0.0")
            print(f"  {heater_name}: TURNED OFF (0% power)")
            return True
        except Exception as e:
            print(f"  Error turning off {heater_name}: {e}")
            return False
    
    def query_heater_status(self, output_num):
        """
        QUERY SINGLE HEATER STATUS
        ==========================
        
        Retrieves and displays current status of specified heater.
        Shows both mode configuration and current power level.
        
        Args:
            output_num (int): Heater output number (1 or 2)
            
        Serial Commands Used:
            OUTMODE? <output> - Gets mode configuration (e.g., "3,0,0")
            MOUT? <output>    - Gets current power percentage
            
        Status Information Retrieved:
            - Mode: Control mode (3=Open Loop)
            - Input: Sensor input (0=None for manual mode)  
            - Powerup: Power cycle behavior (0=Off after restart)
            - Power: Current power percentage (0-100%)
            
        Returns:
            tuple: (mode_string, power_percentage) or (None, None) if error
            Example: ("3,0,0", 75.0) for Open Loop mode at 75% power
        """
        try:
            # Query heater status using centralized method
            # This calls both OUTMODE? and MOUT? commands
            mode, output = self.gl7_controller.query_heater_output_status(output_num)
            
            # Convert power output to float if possible
            try:
                output_val = float(output) if output and output != "NO_RESPONSE" else output
            except (ValueError, TypeError):
                output_val = output
            
            # Display formatted status
            heater_name = "4-pump Heater" if output_num == 1 else "3-pump Heater"
            print(f"  {heater_name} (Output {output_num}): Mode={mode}, Power={output_val}%")
            
            return mode, output_val
        except Exception as e:
            print(f"  Error querying heater output {output_num}: {e}")
            return None, None
    
    def query_all_heaters(self):
        """
        QUERY ALL HEATER STATUS (System Overview)
        ==========================================
        
        Retrieves and displays status of both pump heaters.
        Used for system monitoring and verification after operations.
        
        Returns:
            dict: Complete status of both heaters
                  Format: {1: (mode, power), 2: (mode, power)}
                  Example: {1: ("3,0,0", 75.0), 2: ("3,0,0", 50.0)}
        """
        print("Heater Status:")
        status = {}
        status[1] = self.query_heater_status(1)  # 4-pump heater (Output 1)
        status[2] = self.query_heater_status(2)  # 3-pump heater (Output 2)
        return status
    
    def emergency_stop_all_heaters(self):
        """
        EMERGENCY HEATER SHUTDOWN (Critical Safety Method)
        ==================================================
        
        Immediately shuts down ALL heaters in the system.
        Used for emergency situations, safety protocols, or end-of-operation cleanup.
        
        Safety Features:
        - Turns off both pump heaters (Outputs 1 & 2)
        - Waits for commands to take effect (2 second delay)
        - Verifies shutdown with status confirmation
        - Returns success status for error handling
        
        Usage in GL7 Operations:
        - End of GL7 sequence cleanup
        - Emergency abort situations  
        - Safety interlocks
        - Manual emergency stop via CLI
        
        Returns:
            bool: True if ALL heaters stopped successfully, False if any errors
        """
        print("EMERGENCY HEATER STOP INITIATED")
        print("=" * 50)
        print("Shutting down all heaters...")
        
        # Turn off both heaters and track success
        success_list = []
        success_list.append(self.turn_off_heater(1))  # 4-pump heater
        success_list.append(self.turn_off_heater(2))  # 3-pump heater
        
        # Wait for commands to take effect
        # Lakeshore needs time to process commands
        time.sleep(2)
        
        # Verify shutdown with status confirmation
        print("\nPOST-SHUTDOWN STATUS CONFIRMATION")
        print("=" * 50)
        self.query_all_heaters()
        
        # Return True only if ALL operations successful
        return all(success_list)


# LEGACY FUNCTION WRAPPERS
# ========================
# These functions maintain backward compatibility for older code
# that might still call the old function-based interface.
# NEW CODE SHOULD USE HeaterController CLASS METHODS INSTEAD.

def set_heater_output(gl7_controller, output_num, power_percent):
    """Legacy function - use HeaterController.set_heater_mode_and_power instead"""
    heater_ctrl = HeaterController(gl7_controller)
    return heater_ctrl.set_heater_mode_and_power(output_num, power_percent)

def query_heater_status(gl7_controller, output_num):
    """Legacy function - use HeaterController.query_heater_status instead"""
    heater_ctrl = HeaterController(gl7_controller)
    return heater_ctrl.query_heater_status(output_num)

def emergency_stop_heaters(gl7_controller):
    """Legacy function - use HeaterController.emergency_stop_all_heaters instead"""
    heater_ctrl = HeaterController(gl7_controller)
    return heater_ctrl.emergency_stop_all_heaters()


# COMMAND LINE INTERFACE (CLI) MAIN FUNCTION
# ===========================================
# This function provides direct command-line access to heater control.
# Used when running: python heaters.py <options>

def main():
    """
    MAIN CLI FUNCTION FOR HEATER CONTROL
    ====================================
    
    Provides command-line interface for heater operations.
    
    Usage Examples:
        python heaters.py 1 75        # Set 4-pump heater to 75%
        python heaters.py 2 50        # Set 3-pump heater to 50%
        python heaters.py --both 75 50 # Set both heaters
        python heaters.py --query     # Check status
        python heaters.py --stop      # Emergency stop
        
    Command Line Arguments:
        output: Heater number (1=4-pump, 2=3-pump)
        power: Power percentage (0-100%)
        --both: Set both heaters with two power values
        --query: Display current status without changes
        --stop: Emergency shutdown of all heaters
        --port: Serial port (default /dev/ttyUSB2)
        --baudrate: Communication speed (default 57600)
    """
    parser = argparse.ArgumentParser(description='GL7 Heater Control - Set heater outputs to specified power levels')
    
    # POSITIONAL ARGUMENTS: heater number and power level
    parser.add_argument('output', type=int, choices=[1, 2], nargs='?',
                       help='Heater output number (1 for 4-pump, 2 for 3-pump)')
    parser.add_argument('power', type=float, nargs='?',
                       help='Power percentage (0-100)')
    
    # OPTIONAL ARGUMENTS: special operations
    parser.add_argument('--both', nargs=2, type=float, metavar=('POWER1', 'POWER2'),
                       help='Set both heaters: --both <power1> <power2>')
    parser.add_argument('--query', action='store_true',
                       help='Query current heater status without changing settings')
    parser.add_argument('--stop', action='store_true',
                       help='Emergency stop: immediately shut down both heaters')
    
    # COMMUNICATION SETTINGS: serial port configuration
    parser.add_argument('--port', type=str, default='/dev/ttyUSB2',
                       help='Serial port for Lakeshore 350 (default: /dev/ttyUSB2)')
    parser.add_argument('--baudrate', type=int, default=57600,
                       help='Baud rate for serial communication (default: 57600)')
    
    # PARSE COMMAND LINE ARGUMENTS
    args = parser.parse_args()
    
    # VALIDATE ARGUMENTS: Ensure required parameters are provided
    if not args.query and not args.both and not args.stop and (args.output is None or args.power is None):
        parser.error("Must specify either 'output power', '--both power1 power2', '--query', or '--stop'")
    
    # VALIDATE POWER RANGES: Ensure power values are within 0-100%
    if args.power is not None and (args.power < 0 or args.power > 100):
        parser.error("Power must be between 0 and 100")
    
    if args.both and (any(p < 0 or p > 100 for p in args.both)):
        parser.error("Both power values must be between 0 and 100")
    
    # INITIALIZE COMMUNICATION
    print("Initializing GL7 Heater Control...")
    print(f"Connecting to Lakeshore 350 on {args.port}...")
    
    try:
        # Initialize temperature reader and GL7 controller
        # This establishes serial communication with the Lakeshore 350
        temp_reader = TemperatureReader(port=args.port)
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        # EXECUTE REQUESTED OPERATION
        
        if args.query:
            # QUERY MODE: Display current heater status without changes
            print("\nCurrent Heater Status:")
            query_heater_status(gl7_controller, 1)  # 4-pump heater
            query_heater_status(gl7_controller, 2)  # 3-pump heater
            
        elif args.stop:
            # EMERGENCY STOP MODE: Immediately shut down all heaters
            success = emergency_stop_heaters(gl7_controller)
            if success:
                print("\nEmergency heater stop completed successfully.")
            else:
                print("\nWarning: Some heaters may not have been shut down correctly.")
            
        elif args.both:
            # DUAL HEATER MODE: Set both heaters to specified power levels
            print("\nSetting Both Heaters:")
            success1 = set_heater_output(gl7_controller, 1, args.both[0])  # 4-pump
            success2 = set_heater_output(gl7_controller, 2, args.both[1])  # 3-pump
            
            # Wait for commands to take effect
            time.sleep(1)
            
            # Verify settings by querying status
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
