#!/usr/bin/env python3
"""
GL7 Sorption Cooler Automation Script for Lake Shore 350
Complete automation sequence based on GL7 Manual Section 6.1
Heater commands commented out for safety testing
Stage Temperatures Don't Accurately Reflect Listed Channels/Inputs
"""

import time

class GL7Controller:
    def __init__(self, send_command_func):
        """Initialize with a send_command function from the main controller"""
        self.send_command = send_command_func
        
        # GL7 Configuration mapping
        self.relay_pump_heaters = {1: "4He Pump Heater", 2: "3He Pump Heater"}
        self.analog_heat_switches = {3: "4He Heat Switch", 4: "3He Heat Switch"}

    def read_temperature(self, input_channel):
        """Read temperature from specified input (A, B, C, D)"""
        input_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        if input_channel.upper() in input_map:
            channel_num = input_map[input_channel.upper()]
            response = self.send_command(f"KRDG? {channel_num}")
            try:
                if response and response != "T_OVER":
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
    
    def start_gl7_sequence(self):
        """
        Complete GL7 sorption cooler startup sequence - CORRECTED VERSION
        Based on GL7 manual section 6.1 and 6.2
        NOTE: All heater commands are commented out for safety
        """
        print("=" * 60)
        print("GL7 SORPTION COOLER STARTUP SEQUENCE")
        print("=" * 60)
        print("Based on GL7 Manual Section 6.1 - Operating Steps")
        print("NOTE: All heater activation commands are COMMENTED OUT for safety")
        print("This is a simulation showing the correct process flow\n")
        
        # Stage 1: Initial Status Check
        print("STAGE 1: INITIAL STATUS CHECK")
        print("-" * 30)
        
        # Check starting temperatures
        temp_4k = self.read_temperature('A')  # 4K stage
        temp_1k = self.read_temperature('B')  # 1K stage  
        temp_100mk = self.read_temperature('C')  # 100mK stage
        
        print(f"4K Stage Temperature (Input A): {temp_4k} K")
        print(f"1K Stage Temperature (Input B): {temp_1k} K") 
        print(f"100mK Stage Temperature (Input C): {temp_100mk} K")
        
        # Check current heater/switch status
        print("\nCurrent Heater/Switch Status:")
        for relay_num, name in self.relay_pump_heaters.items():
            config, status = self.query_relay_status(relay_num)
            print(f"  {name} (Relay {relay_num}): Config={config}, Status={status}")
        
        for output_num, name in self.analog_heat_switches.items():
            config = self.query_analog_status(output_num)
            print(f"  {name} (Analog {output_num}): Config={config}")
        
        print("\n")
        time.sleep(2)
        
        # Stage 2: Pre-cooling Phase (Room Temp to 4K)
        print("STAGE 2: PRE-COOLING PHASE (Room Temperature → 4K)")
        print("-" * 50)
        print("Manual: 'Pre-cool from room temperature to ~4K'")
        print("Waiting for dilution refrigerator to cool down...")
        
        # Monitor cooling progression
        print("Monitoring pre-cooling progression...")
        for check in range(1, 4):
            temp_4k = self.read_temperature('A')
            print(f"  Check {check}: 4K Stage = {temp_4k} K")
            
            if isinstance(temp_4k, float):
                if temp_4k > 50:
                    print("    → Still warming up from room temperature")
                elif temp_4k > 10:
                    print("    → Cooling down, approaching heat switch transition")
                elif temp_4k <= 10:
                    print("    ✓ Heat switches will turn OFF (< 10K)")
                    break
            time.sleep(1)
        
        print("\n")
        
        # Stage 3: Heat Switch Transition (< 10K)
        print("STAGE 3: HEAT SWITCH TRANSITION (< 10K)")
        print("-" * 40)
        print("Manual: 'During pre-cooling, when both heat switches turn OFF (< 10K)'")
        print("Heat switches automatically turn OFF when temperature < 10K")
        
        # Check if we're at the transition point
        temp_4k = self.read_temperature('A')
        if isinstance(temp_4k, float) and temp_4k <= 10:
            print(f"✓ Current temperature ({temp_4k} K) < 10K")
            print("✓ Heat switches have turned OFF automatically")
            print("→ Ready to activate pump heaters")
        else:
            print(f"Current temperature: {temp_4k} K")
            print("Waiting for temperature < 10K...")
        
        print("\n")
        time.sleep(2)
        
        # Stage 4: Pump Heating Phase (45-55K)
        print("STAGE 4: PUMP HEATING PHASE")
        print("-" * 30)
        print("Manual: 'heat both pumps to around 45-55K and keep them at that temperature'")
        print("Manual: 'until the heads cool to ~4K and their temperature stabilises'")
        
        # Activate both pump heaters
        print("Activating BOTH pump heaters to 45-55K:")
        
        print(f"  Starting {self.relay_pump_heaters[1]} (Relay 1):")
        print("    Command would be: RELAY 1,1  # Turn ON 4He pump heater")
        # COMMENTED OUT: self.send_command("RELAY 1,1")
        print("    → 4He pump heating to 45-55K")
        
        print(f"  Starting {self.relay_pump_heaters[2]} (Relay 2):")
        print("    Command would be: RELAY 2,1  # Turn ON 3He pump heater") 
        # COMMENTED OUT: self.send_command("RELAY 2,1")
        print("    → 3He pump heating to 45-55K")
        
        print("\nBoth pumps now heating - waiting for 4K stage to stabilize...")
        
        # Monitor cooling to 4K while pumps are heated
        for minute in range(1, 6):
            temp_4k = self.read_temperature('A')
            temp_1k = self.read_temperature('B')
            print(f"  Minute {minute}: 4K Stage = {temp_4k} K, 1K Stage = {temp_1k} K")
            print(f"              Pumps maintained at 45-55K")
            
            if isinstance(temp_4k, float) and temp_4k <= 4.0:
                print("    ✓ 4K stage has reached ~4K and is stabilizing")
                break
            time.sleep(1)
        
        print("\n")
        time.sleep(2)
        
        # Stage 5: 4He Pump Transition
        print("STAGE 5: 4He PUMP TRANSITION")
        print("-" * 30)
        print("Manual: 'Turn OFF the 4-pump heat and turn ON the 4-switch'")
        
        # Turn off 4He pump heater
        print(f"Turning OFF {self.relay_pump_heaters[1]}:")
        print("  Command would be: RELAY 1,0  # Turn OFF 4He pump heater")
        # COMMENTED OUT: self.send_command("RELAY 1,0")
        print("  → 4He pump heater DEACTIVATED")
        
        time.sleep(1)
        
        # Turn on 4He heat switch
        print(f"Turning ON {self.analog_heat_switches[3]}:")
        print("  Command would be: ANALOG 3,1,1,5.0,0.0,0  # Turn ON 4He switch (5V)")
        # COMMENTED OUT: self.send_command("ANALOG 3,1,1,5.0,0.0,0")
        print("  → 4He heat switch ACTIVATED (5V)")
        print("  → Heads will cool rapidly below 1K")
        
        print("\n")
        time.sleep(2)
        
        # Stage 6: Cooling to 2K
        print("STAGE 6: COOLING TO < 2K")
        print("-" * 25)
        print("Manual: 'When the heads have cooled to less than 2K'")
        print("Monitoring head temperatures...")
        
        for check in range(1, 4):
            temp_4k = self.read_temperature('A')
            temp_1k = self.read_temperature('B')
            print(f"  Check {check}: 4K Stage = {temp_4k} K, 1K Stage = {temp_1k} K")
            
            if isinstance(temp_1k, float) and temp_1k <= 2.0:
                print("    ✓ Heads have cooled to < 2K")
                break
            elif isinstance(temp_1k, float):
                print(f"    → Still cooling (1K stage at {temp_1k:.2f} K)")
            time.sleep(1)
        
        print("\n")
        time.sleep(2)
        
        # Stage 7: 3He Pump Transition
        print("STAGE 7: 3He PUMP TRANSITION")
        print("-" * 30)
        print("Manual: 'turn OFF the 3-pump heater and turn ON the 3-switch'")
        
        # Turn off 3He pump heater
        print(f"Turning OFF {self.relay_pump_heaters[2]}:")
        print("  Command would be: RELAY 2,0  # Turn OFF 3He pump heater")
        # COMMENTED OUT: self.send_command("RELAY 2,0")
        print("  → 3He pump heater DEACTIVATED")
        
        time.sleep(1)
        
        # Turn on 3He heat switch
        print(f"Turning ON {self.analog_heat_switches[4]}:")
        print("  Command would be: ANALOG 4,1,1,5.0,0.0,0  # Turn ON 3He switch (5V)")
        # COMMENTED OUT: self.send_command("ANALOG 4,1,1,5.0,0.0,0")
        print("  → 3He heat switch ACTIVATED (5V)")
        print("  → Final cooldown to ~300mK begins")
        
        print("\n")
        time.sleep(2)
        
        # Stage 8: Final Cooldown Monitoring
        print("STAGE 8: FINAL COOLDOWN TO ~300mK")
        print("-" * 35)
        print("Monitoring final temperature progression...")
        
        for cycle in range(1, 4):
            temp_4k = self.read_temperature('A')
            temp_1k = self.read_temperature('B')
            temp_100mk = self.read_temperature('C')
            
            print(f"  Cycle {cycle}:")
            print(f"    4K Stage: {temp_4k} K")
            print(f"    1K Stage: {temp_1k} K")
            print(f"    100mK Stage: {temp_100mk} K")
            
            if isinstance(temp_100mk, float) and temp_100mk < 0.5:
                print("    ✓ Approaching 300mK target!")
                break
            elif isinstance(temp_100mk, float):
                print(f"    → Cooling toward 300mK target")
            time.sleep(1)
        
        print("\n")
        
        # Stage 9: Final Status
        print("STAGE 9: FINAL STATUS CHECK")
        print("-" * 30)
        
        # Final temperature readings
        temp_4k = self.read_temperature('A')
        temp_1k = self.read_temperature('B')
        temp_100mk = self.read_temperature('C')
        
        print("Final Temperatures:")
        print(f"  4K Stage (Input A): {temp_4k} K")
        print(f"  1K Stage (Input B): {temp_1k} K") 
        print(f"  100mK Stage (Input C): {temp_100mk} K")
        
        # Final heater/switch status
        print("\nFinal Heater/Switch Status:")
        for relay_num, name in self.relay_pump_heaters.items():
            config, status = self.query_relay_status(relay_num)
            expected = "OFF" if relay_num in [1, 2] else "Current Status"
            print(f"  {name}: {status} (should be OFF)")
        
        for output_num, name in self.analog_heat_switches.items():
            config = self.query_analog_status(output_num)
            expected = "ON" if output_num in [3, 4] else "Current Status"
            print(f"  {name}: Config={config} (should be ON)")
        
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
