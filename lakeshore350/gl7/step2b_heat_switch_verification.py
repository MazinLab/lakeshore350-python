#!/usr/bin/env python3
"""
GL7 Step 2B: Heat Switch Status Verification
"""

import time

def execute_step2b(gl7_controller):
    """Execute GL7 Step 2b: Heat Switch Verification"""
    print("GL7 STEP 2B: HEAT SWITCH VERIFICATION")
    print("-" * 40)
    print("Verifying heat switches turn OFF when heads reach ~10K...")
    print("This step checks temperatures and heat switch status before proceeding to pump heating.\n")
    
    # Temperature Check - Read all temperatures first
    print("Temperature Check:")
    
    # 3He Head temperature (Input A)
    temp_3he_head = gl7_controller.read_temperature('A')
    print(f"  3-head Temperature (Input A): {temp_3he_head} K")
    
    # 4He Head temperature (Input C)
    temp_4he_head = gl7_controller.read_temperature('C')
    print(f"  4-head Temperature (Input C): {temp_4he_head} K")
    
    # 4K stage temperature (Channel 2)
    temp_channel_2 = gl7_controller.send_command("KRDG? 2")
    try:
        if temp_channel_2 and temp_channel_2 != "T_OVER":
            temp_4k_stage = float(temp_channel_2)
        else:
            temp_4k_stage = temp_channel_2
    except ValueError:
        temp_4k_stage = temp_channel_2
    print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
    
    # 50K stage temperature (Channel 3)
    temp_channel_3 = gl7_controller.send_command("KRDG? 3")
    try:
        if temp_channel_3 and temp_channel_3 != "T_OVER":
            temp_50k_stage = float(temp_channel_3)
        else:
            temp_50k_stage = temp_channel_3
    except ValueError:
        temp_50k_stage = temp_channel_3
    print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
    
    # Heat Switch Status
    print("\nHeat Switch Status:")
    for output_num, name in gl7_controller.analog_heat_switches.items():
        config = gl7_controller.query_analog_status(output_num)
        print(f"  {name} (Analog {output_num}): {config}")
    
    print()
    
    # User confirmation before proceeding to pump heating
    input("Press ENTER to confirm both heat switches are OFF and proceed to Step 3 (Pump Heating)...")
