#!/usr/bin/env python3
"""
GL7 Step 3: Pump Heating Phase
"""

import time

def execute_step3(gl7_controller):
    """Execute GL7 Step 3: Pump Heating Phase (45-55K)"""
    print("GL7 STEP 3: PUMP HEATING PHASE")
    print("-" * 35)
    print("Confirm fridge is ~10K and both switches are OFF before proceeding...")
    
    # User confirmation before starting heaters
    input("\nPress ENTER when ready to start 4-pump heater...")
    
    # Get user input for 4-pump heater percentage
    while True:
        try:
            power_4pump = input("Enter 4-pump heater power percentage (0-100)... ")
            power_4pump = float(power_4pump)
            if 0 <= power_4pump <= 100:
                break
            else:
                print("Please enter a value between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"  Starting 4-pump Heater (Heater Output 1):")
    gl7_controller.send_command("OUTMODE 1,3,0,0")
    gl7_controller.send_command(f"MOUT 1,{power_4pump}")
    print(f"    → 4-pump Heater at {power_4pump}% power")
    
    # Wait for user confirmation before starting second heater
    input("\nPress ENTER when ready to start 3-pump heater...")
    
    # Get user input for 3-pump heater percentage
    while True:
        try:
            power_3pump = input("Enter 3-pump heater power percentage (0-100): ")
            power_3pump = float(power_3pump)
            if 0 <= power_3pump <= 100:
                break
            else:
                print("Please enter a value between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    print(f"  Starting 3-pump Heater (Heater Output 2)...")
    gl7_controller.send_command("OUTMODE 2,3,0,0")
    gl7_controller.send_command(f"MOUT 2,{power_3pump}")
    print(f"    → 3-pump Heater at {power_3pump}% power")
    
    print("\nBoth pumps now heating...")
    print("Waiting for 3-head (Input A) and 4-head (Input C) to reach 4K...")
    
    # Single temperature check for demonstration
    print(f"\nTemperature Check:")
    
    # Read head thermometers
    temp_3he_head = gl7_controller.read_temperature('A')  # 3-head
    temp_4he_head = gl7_controller.read_temperature('C')  # 4-head
    
    print(f"  3-head Temperature (Input A): {temp_3he_head} K")
    print(f"  4-head Temperature (Input C): {temp_4he_head} K")
    
    # Also read stage temperatures
    temp_4k_stage = gl7_controller.read_temperature('D2')     # 4K stage (Input D2)
    temp_50k_stage = gl7_controller.read_temperature('D3')    # 50K stage (Input D3)  
    temp_input_b = gl7_controller.read_temperature('B')       # Device stage
    
    print(f"  4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    print(f"  Device Stage Temperature (Input B): {temp_input_b} K")
    
    # 3-pump temperature (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    print(f"  3-pump Temperature (Input D): {temp_3pump} K")
    
    # 4-pump temperature (Channel 5)
    temp_4pump = gl7_controller.send_command("KRDG? 5")
    try:
        if temp_4pump and temp_4pump != "T_OVER":
            temp_4pump_val = float(temp_4pump)
        else:
            temp_4pump_val = temp_4pump
    except ValueError:
        temp_4pump_val = temp_4pump
    print(f"  4-pump Temperature (Channel 5): {temp_4pump_val} K")
    
    # Check if heads have reached 4K (for assessment logic only)
    heads_at_4k = []
    if isinstance(temp_3he_head, float) and temp_3he_head <= 4.0:
        heads_at_4k.append("3He")
    if isinstance(temp_4he_head, float) and temp_4he_head <= 4.0:
        heads_at_4k.append("4-head")

    
    # Check current heater status
    print("\nHeater Status:")
    mode_1, output_1 = gl7_controller.query_heater_output_status(1)
    try:
        output_1_val = float(output_1) if output_1 and output_1 != "NO_RESPONSE" else 0.0
        print(f"  4-pump Heater (Output 1): Mode={mode_1}, Output={output_1_val}%")
    except (ValueError, TypeError):
        print(f"  4-pump Heater (Output 1): Mode={mode_1}, Output={output_1}")
    
    mode_2, output_2 = gl7_controller.query_heater_output_status(2)
    try:
        output_2_val = float(output_2) if output_2 and output_2 != "NO_RESPONSE" else 0.0
        print(f"  3-pump Heater (Output 2): Mode={mode_2}, Output={output_2_val}%")
    except (ValueError, TypeError):
        print(f"  3-pump Heater (Output 2): Mode={mode_2}, Output={output_2}")
    
    print("→ Ready to proceed to 4-pump Heater transition")
    
    print(f"\nStep 3 Summary:")
    print(f"  4-pump Heater set to: {power_4pump}% power")
    print(f"  3-pump Heater set to: {power_3pump}% power")
    
    # User confirmation before proceeding to Step 4
    input("\nPress ENTER to confirm heads have reached 4K and proceed to Step 4, 4-pump Transition ...")
