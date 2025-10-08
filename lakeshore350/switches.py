#!/usr/bin/env python3
"""
GL7 HEAT SWITCH CONTROL MODULE
==============================

OVERVIEW:
---------
This module provides centralized control of heat switches in the GL7 sorption cooler system.
Heat switches are critical for thermal isolation and connection between different temperature stages.

HARDWARE MAPPING:
-----------------
- Switch 3 (4-switch): Controls 4K stage heat switch → Analog Output 3
- Switch 4 (3-switch): Controls 3He stage heat switch → Analog Output 4

SWITCH STATES:
--------------
- ON (5V):  Heat switch closed → thermal connection established
- OFF (0V): Heat switch open → thermal isolation maintained

LAKESHORE COMMANDS USED:
------------------------
- ANALOG: Controls analog outputs 3 & 4 for heat switch voltage control

ARCHITECTURE:
-------------
All heat switch serial commands are centralized in the SwitchController class.
This ensures consistent switch control and eliminates scattered ANALOG commands
throughout the GL7 step files.

USAGE:
------
from lakeshore350.switches import SwitchController
controller = SwitchController(gl7_controller)
controller.turn_on_switch(3)   # Turn on 4-switch
controller.turn_off_switch(4)  # Turn off 3-switch
"""

import argparse
import sys
import time

# IMPORT HANDLING
# ===============
# Handle imports for both direct execution and module import
try:
    # When imported as module (normal operation)
    from .gl7_control import GL7Controller
    from .temperature import TemperatureReader
except ImportError:
    # When run directly (python switches.py)
    from gl7_control import GL7Controller
    from temperature import TemperatureReader


# MAIN SWITCH CONTROLLER CLASS
# ============================
class SwitchController:
    """
    CENTRALIZED HEAT SWITCH CONTROLLER
    ==================================
    
    All heat switch operations go through this class to maintain:
    - Single point of control for all switch operations
    - Consistent error handling and logging
    - Centralized serial command management
    - Clear separation between GL7 logic and hardware control
    """
    
    def __init__(self, gl7_controller):
        """
        INITIALIZE SWITCH CONTROLLER
        ============================
        
        Args:
            gl7_controller: GL7Controller instance for serial communication
        """
        self.gl7_controller = gl7_controller
        
    def turn_on_switch(self, switch_num):
        """
        TURN ON HEAT SWITCH (CLOSE THERMAL CONNECTION)
        ==============================================
        
        Sets analog output to 5V to activate the heat switch.
        When ON, the switch provides thermal connection between stages.
        
        Args:
            switch_num (int): Switch number (3 for 4-switch, 4 for 3-switch)
            
        Returns:
            bool: True if successful, False otherwise
            
        Hardware Mapping:
            switch_num=3 → 4-switch → Analog Output 3 → 4K stage heat switch
            switch_num=4 → 3-switch → Analog Output 4 → 3He stage heat switch
            
        ANALOG Command Format:
            ANALOG <output>,<input>,<source>,<high_value>,<low_value>,<manual_value>
            - output: Analog output number (3 or 4)
            - input: 1 = manual mode
            - source: 1 = manual mode  
            - high_value: 5.0V (switch ON voltage)
            - low_value: 0.0V (not used in manual mode)
            - manual_value: 0 (not used when high_value specified)
        """
        # DETERMINE SWITCH IDENTITY
        switch_name = "4-switch" if switch_num == 3 else "3-switch"
        analog_output = switch_num  # 3 for 4-switch, 4 for 3-switch
        
        print(f"Turning ON {switch_name} (Analog Output {analog_output}):")
        
        try:
            # SEND ANALOG COMMAND TO TURN ON SWITCH
            # ANALOG 3,1,1,5.0,0.0,0 → Turn on 4-switch (5V)
            # ANALOG 4,1,1,5.0,0.0,0 → Turn on 3-switch (5V)
            self.gl7_controller.send_command(f"ANALOG {analog_output},1,1,5.0,0.0,0")
            print(f"  → {switch_name} ACTIVATED (5V)")
            return True
        except Exception as e:
            print(f"  Error turning on {switch_name}: {e}")
            return False
    
    def turn_off_switch(self, switch_num):
        """
        TURN OFF HEAT SWITCH (OPEN THERMAL CONNECTION)
        ===============================================
        
        Sets analog output to 0V to deactivate the heat switch.
        When OFF, the switch provides thermal isolation between stages.
        
        Args:
            switch_num (int): Switch number (3 for 4-switch, 4 for 3-switch)
            
        Returns:
            bool: True if successful, False otherwise
            
        Hardware Mapping:
            switch_num=3 → 4-switch → Analog Output 3 → 4K stage heat switch
            switch_num=4 → 3-switch → Analog Output 4 → 3He stage heat switch
            
        ANALOG Command Format:
            ANALOG <output>,0 → Simplified form sets output to 0V
            - output: Analog output number (3 or 4) 
            - 0: Sets output to 0V (OFF state)
        """
        # DETERMINE SWITCH IDENTITY
        switch_name = "4-switch" if switch_num == 3 else "3-switch"
        analog_output = switch_num  # 3 for 4-switch, 4 for 3-switch
        
        print(f"Turning OFF {switch_name} (Analog Output {analog_output}):")
        
        try:
            # SEND ANALOG COMMAND TO TURN OFF SWITCH
            # ANALOG 3,0 → Turn off 4-switch (0V)
            # ANALOG 4,0 → Turn off 3-switch (0V)
            self.gl7_controller.send_command(f"ANALOG {analog_output},0")
            print(f"  → {switch_name} DEACTIVATED (0V)")
            return True
        except Exception as e:
            print(f"  Error turning off {switch_name}: {e}")
            return False
    
    def set_switch_state(self, switch_num, state):
        """
        SET HEAT SWITCH STATE (GENERIC ON/OFF CONTROL)
        ==============================================
        
        Convenience method to set switch state using string commands.
        Routes to appropriate turn_on_switch() or turn_off_switch() method.
        
        Args:
            switch_num (int): Switch number (3 for 4-switch, 4 for 3-switch)
            state (str): "ON" or "OFF" (case insensitive)
            
        Returns:
            bool: True if successful, False otherwise
            
        Usage Examples:
            controller.set_switch_state(3, "ON")   # Turn on 4-switch
            controller.set_switch_state(4, "off")  # Turn off 3-switch
        """
        if state.upper() == "ON":
            return self.turn_on_switch(switch_num)
        elif state.upper() == "OFF":
            return self.turn_off_switch(switch_num)
        else:
            switch_name = "4-switch" if switch_num == 3 else "3-switch"
            print(f"  Error: Invalid state '{state}' for {switch_name}. Use 'ON' or 'OFF'")
            return False
    
    def query_switch_status(self, switch_num):
        """
        QUERY HEAT SWITCH STATUS
        ========================
        
        Reads current switch configuration and determines ON/OFF state.
        Uses ANALOG? command to get current analog output settings.
        
        Args:
            switch_num (int): Switch number (3 for 4-switch, 4 for 3-switch)
            
        Returns:
            tuple: (config, status_text) or (None, None) if error
            - config: Raw configuration string from Lakeshore
            - status_text: Human-readable status ("ON (5V)", "OFF (0V)", etc.)
            
        ANALOG? Response Format:
            Returns analog output configuration showing current voltage setting
        """
        try:
            # DETERMINE SWITCH IDENTITY
            switch_name = "4-switch" if switch_num == 3 else "3-switch"
            analog_output = switch_num  # 3 for 4-switch, 4 for 3-switch
            
            # QUERY ANALOG OUTPUT STATUS
            config = self.gl7_controller.query_analog_status(analog_output)
            
            # PARSE CONFIGURATION TO DETERMINE ON/OFF STATUS
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
            switch_name = "4-switch" if switch_num == 3 else "3-switch"
            print(f"  Error querying {switch_name}: {e}")
            return None, None
    
    def query_all_switches(self):
        """
        QUERY STATUS OF ALL HEAT SWITCHES
        =================================
        
        Queries both 4-switch (output 3) and 3-switch (output 4) and
        displays their current status in a formatted report.
        
        Returns:
            dict: Status of both switches {3: (config, status), 4: (config, status)}
            - Key 3: 4-switch status (config string, status text)
            - Key 4: 3-switch status (config string, status text)
            
        Usage:
            status = controller.query_all_switches()
            # Displays:
            # Heat Switch Status:
            #   4-switch (Analog Output 3): ON (5.0V)
            #   3-switch (Analog Output 4): OFF (0.0V)
        """
        print("Heat Switch Status:")
        status = {}
        status[3] = self.query_switch_status(3)  # 4-switch
        status[4] = self.query_switch_status(4)  # 3-switch
        return status
    
    def turn_off_all_switches(self):
        """
        TURN OFF ALL HEAT SWITCHES (EMERGENCY ISOLATION)
        ===============================================
        
        Safety function to immediately turn off both heat switches.
        Provides thermal isolation of all stages.
        
        Returns:
            bool: True if all switches turned off successfully
            
        Used for:
        - Emergency stops
        - End of GL7 procedures
        - Safety isolation
        """
        print("Turning OFF all heat switches...")
        success_list = []
        success_list.append(self.turn_off_switch(3))  # 4-switch
        success_list.append(self.turn_off_switch(4))  # 3-switch
        return all(success_list)
    
    def turn_on_all_switches(self):
        """
        TURN ON ALL HEAT SWITCHES (THERMAL CONNECTION)
        ==============================================
        
        Utility function to turn on both heat switches simultaneously.
        Establishes thermal connection between all stages.
        
        Returns:
            bool: True if all switches turned on successfully
            
        Used for:
        - System warmup procedures
        - Thermal equilibration
        - Testing operations
        """
        print("Turning ON all heat switches...")
        success_list = []
        success_list.append(self.turn_on_switch(3))  # 4-switch
        success_list.append(self.turn_on_switch(4))  # 3-switch
        return all(success_list)


# LEGACY FUNCTION WRAPPERS
# ========================
# These functions maintain backward compatibility for older code
# that might still call the old function-based interface.
# NEW CODE SHOULD USE SwitchController CLASS METHODS INSTEAD.

def set_switch_state(gl7_controller, switch_num, state):
    """Legacy function - use SwitchController.set_switch_state instead"""
    switch_ctrl = SwitchController(gl7_controller)
    return switch_ctrl.set_switch_state(switch_num, state)

def query_switch_status(gl7_controller, switch_num):
    """Legacy function - use SwitchController.query_switch_status instead"""
    switch_ctrl = SwitchController(gl7_controller)
    return switch_ctrl.query_switch_status(switch_num)


# COMMAND LINE INTERFACE (CLI) MAIN FUNCTION
# ===========================================
# This function provides direct command-line access to switch control.
# Used when running: python switches.py <options>

def main():
    """
    MAIN CLI FUNCTION FOR SWITCH CONTROL
    ====================================
    
    Provides command-line interface for heat switch operations.
    
    Command Examples:
        python switches.py 3 ON          # Turn on 4-switch
        python switches.py 4 OFF         # Turn off 3-switch  
        python switches.py --both ON     # Turn on both switches
        python switches.py --query       # Query all switches
        python switches.py --off-all     # Turn off all switches
    """
    # ARGUMENT PARSER SETUP
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
    
    # VALIDATE COMMAND LINE ARGUMENTS
    if not args.query and not args.both and (args.switch is None or args.state is None):
        parser.error("Must specify either 'switch state', '--both ON/OFF', or '--query'")
    
    print("Initializing GL7 Heat Switch Control...")
    print(f"Connecting to Lakeshore 350 on {args.port}...")
    
    try:
        # INITIALIZE HARDWARE CONNECTIONS
        # Create temperature reader for serial communication
        temp_reader = TemperatureReader(port=args.port)
        # Create GL7 controller using the temperature reader's send_command method
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        if args.query:
            # QUERY MODE - Show current status without changes
            print("\nCurrent Heat Switch Status:")
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
            
        elif args.both:
            # BOTH SWITCHES MODE - Set both switches to same state
            state = args.both.upper()
            set_switch_state(gl7_controller, 3, state)  # 4-switch
            set_switch_state(gl7_controller, 4, state)  # 3-switch
            
            # Wait for commands to take effect
            time.sleep(1)
            
            # Show status of both switches after change
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
                
        else:
            # SINGLE SWITCH MODE - Set individual switch
            state = args.state.upper()
            set_switch_state(gl7_controller, args.switch, state)
            
            # Wait for command to take effect
            time.sleep(1)
            
            # Show status of both switches after change
            query_switch_status(gl7_controller, 3)  # 4-switch
            query_switch_status(gl7_controller, 4)  # 3-switch
        
        # CLEANUP - Close serial connection
        temp_reader.close()
        print("\nConnection closed.")
        
    except Exception as e:
        # ERROR HANDLING - Critical error during switch operations
        print(f"\nCRITICAL ERROR during switch control: {e}")
        print("Manual intervention may be required!")
        sys.exit(1)


# ENTRY POINT FOR DIRECT EXECUTION
# =================================
if __name__ == "__main__":
    main()
