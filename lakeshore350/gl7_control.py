#!/usr/bin/env python3
"""
GL7 Sorption Cooler Automation Script for Lake Shore 350
Complete automation sequence ed on GL7 Manual Section 6.1
Heater commands commented out for safety testing
Stage Temperatures Don't Accurately Reflect Listed Channels/Inputs
"""

import time
from .gl7 import (
    execute_step1, execute_step2a, execute_step2b, execute_step3, 
    execute_step4, execute_step5, execute_step6
)

class GL7Controller:
    def __init__(self, send_command_func):
        """Initialize with a send_command function from the main controller"""
        self.send_command = send_command_func
        
        # GL7 Configuration mapping
        self.relay_pump_heaters = {1: "4He Pump Heater", 2: "3He Pump Heater"}
        self.analog_heat_switches = {3: "4-switch", 4: "3-switch"}

    def read_temperature(self, input_channel):
        """Read temperature from specified input (A, B, C, D, D2, D3)
        For GL7 3-head (A) and 4-head (C), returns resistance in ohms.
        For other inputs, returns temperature in Kelvin.
        Special inputs D2 and D3 are used for 4K and 50K stage temperatures.
        """
        # Handle special D2 and D3 inputs for stage temperatures
        if isinstance(input_channel, str) and input_channel.upper() in ['D2', 'D3']:
            # Check reading status first to detect over-range conditions
            status_response = self.send_command(f"RDGST? {input_channel.upper()}")
            try:
                if status_response:
                    status_code = int(status_response)
                    # Status code with bit 5 set (32 or higher) indicates temperature over-range
                    if status_code & 32:  # Check if bit 5 is set
                        return "T_OVER"
            except ValueError:
                pass
            
            # If status is normal, get the temperature reading
            response = self.send_command(f"KRDG? {input_channel.upper()}")
            try:
                if response and response != "T_OVER":
                    temp_value = float(response)
                    # Double-check: treat 0.0 readings as over-range for temperature sensors
                    if temp_value == 0.0:
                        return "T_OVER"
                    return temp_value
                else:
                    return response
            except ValueError:
                return response
        
        # Handle regular inputs (A, B, C, D)
        input_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        if isinstance(input_channel, str) and input_channel.upper() in input_map:
            channel_num = input_map[input_channel.upper()]
            
            # For GL7 3-head (A) and 4-head (C), read resistance instead of temperature
            if input_channel.upper() in ['A', 'C']:
                response = self.send_command(f"SRDG? {channel_num}")
            else:
                response = self.send_command(f"KRDG? {channel_num}")
                
            try:
                if response and response != "T_OVER":
                    return float(response)
                else:
                    return response
            except ValueError:
                return response
        
        # Handle numeric channels/inputs directly
        elif isinstance(input_channel, int):
            response = self.send_command(f"KRDG? {input_channel}")
            try:
                if response and response != "T_OVER":
                    return float(response)
                else:
                    return response
            except ValueError:
                return response
        return None
    
    def read_resistance(self, input_channel):
        """Read resistance from specified input (A, B, C, D)"""
        input_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        if input_channel.upper() in input_map:
            channel_num = input_map[input_channel.upper()]
            response = self.send_command(f"SRDG? {channel_num}")
            try:
                if response and response != "T_OVER":
                    return float(response)
                else:
                    return response
            except ValueError:
                return response
        return None

    def read_voltage(self, input_channel):
        """Read voltage from specified input (A, B, C, D)"""
        input_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        if input_channel.upper() in input_map:
            channel_num = input_map[input_channel.upper()]
            response = self.send_command(f"VRDG? {channel_num}")
            try:
                if response and response != "V_OVER":
                    return float(response)
                else:
                    return response
            except ValueError:
                return response
        return None
    
    def query_relay_status(self, relay_num):
        """Query relay heater status"""
        config = self.send_command(f"RELAY? {relay_num}")
        status = self.send_command(f"RELAYST? {relay_num}")
        return config, status
    
    def query_analog_status(self, output_num):
        """Query analog output status"""
        config = self.send_command(f"ANALOG? {output_num}")
        return config
    
    def query_heater_output_status(self, output_num):
        """Query the status of a heater output (mode and current level)"""
        # Get the output mode (0=Off, 1=Monitor Out, 2=Open Loop, 3=Zone, 4=Still, 5=Closed Loop PID, 6=Closed Loop PI)
        mode = self.send_command(f"OUTMODE? {output_num}")
        # Get the manual output percentage (for Open Loop mode)
        manual_output = self.send_command(f"MOUT? {output_num}")
        return mode, manual_output
    
    def start_gl7_sequence(self):
        """
        Complete GL7 sorption cooler startup sequence - MODULAR VERSION
        Based on GL7 manual section 6.1 and 6.2
        NOTE: All heater commands are commented out for safety
        """
        print("=" * 60)
        print("GL7 SORPTION COOLER STARTUP SEQUENCE")
        print("=" * 60)
        print("Based on GL7 Manual Section 6.1 - Operating Steps")
        print("NOTE: All heater activation commands are COMMENTED OUT for safety")
        print("This is a simulation showing the correct process flow\n")
        
        # Execute all steps in sequence
        execute_step1(self)
        execute_step2a(self)
        execute_step2b(self)
        execute_step3(self)
        execute_step4(self)
        execute_step5(self)
        execute_step6(self)
        
        print("\n" + "=" * 60)
        print("GL7 STARTUP SEQUENCE SIMULATION COMPLETE")
        print("=" * 60)
        print("CORRECT SEQUENCE SUMMARY:")
        print("1. Pre-cool from room temp to 4K")
        print("2. At 10K: Heat switches turn OFF automatically")
        print("3. Heat BOTH pumps to 45-55K until 4K stage stabilizes")
        print("4. Turn OFF 4He pump heater, turn ON 4He switch")
        print("5. At <2K: Turn OFF 3He pump heater, turn ON 3He switch")
        print("6. System cools to ~300mK")
        print("\nNOTE: This was a SIMULATION - no heaters were activated")
        print("To enable actual control, uncomment the send_command() calls")
        
        return True
    
    # Individual step execution methods for manual control
    def execute_step1(self):
        """Execute GL7 Step 1: Initial Status Check"""
        return execute_step1(self)
    
    def execute_step2a(self):
        """Execute GL7 Step 2A: Pre-cooling Phase"""
        return execute_step2a(self)
    
    def execute_step2b(self):
        """Execute GL7 Step 2B: Heat Switch Status Verification"""
        return execute_step2b(self)
    
    def execute_step3(self):
        """Execute GL7 Step 3: Pump Heating Phase"""
        return execute_step3(self)
    
    def execute_step4(self):
        """Execute GL7 Step 4: 4He Pump Transition"""
        return execute_step4(self)
    
    def execute_step5(self):
        """Execute GL7 Step 5: Cooling to 2K and 3He Pump Transition"""
        return execute_step5(self)
    
    def execute_step6(self):
        """Execute GL7 Step 6: Final Cooldown Monitoring"""
        return execute_step6(self)
    
    def execute_step7(self):
        """Execute GL7 Step 7: Final Status Check"""
        return execute_step7(self)
