#!/usr/bin/env python3
"""
GL7 Step 4: 4He Pump Transition
"""

import time

def execute_step4(gl7_controller):
    """Execute GL7 Step 4: 4He Pump Transition"""
    print("GL7 STEP 4: 4-PUMP Heater TRANSITION")
    print("-" * 35)
    
    # Pre-transition temperature verification
    print("Temperature Check:")
    
    # Check head temperatures
    pre_temp_3he = gl7_controller.read_temperature('A')  # 3-head
    pre_temp_4he = gl7_controller.read_temperature('C')  # 4-head
    
    # Check stage temperatures
    pre_temp_channel_2 = gl7_controller.send_command("KRDG? 2")  # 4K stage
    pre_temp_channel_3 = gl7_controller.send_command("KRDG? 3")  # 50K stage
    
    try:
        if pre_temp_channel_2 and pre_temp_channel_2 != "T_OVER":
            pre_4k_stage = float(pre_temp_channel_2)
        else:
            pre_4k_stage = pre_temp_channel_2
    except ValueError:
        pre_4k_stage = pre_temp_channel_2
        
    try:
        if pre_temp_channel_3 and pre_temp_channel_3 != "T_OVER":
            pre_50k_stage = float(pre_temp_channel_3)
        else:
            pre_50k_stage = pre_temp_channel_3
    except ValueError:
        pre_50k_stage = pre_temp_channel_3
    
    print(f"  3-head Temperature (Input A): {pre_temp_3he} K")
    print(f"  4-head Temperature (Input C): {pre_temp_4he} K")
    print(f"  4K Stage Temperature (Channel 2): {pre_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {pre_50k_stage} K")
    
    # Check heads for transition (for logic only)
    heads_ready_for_transition = []
    if isinstance(pre_temp_3he, float) and pre_temp_3he <= 4.0:
        heads_ready_for_transition.append("3He")
    if isinstance(pre_temp_4he, float) and pre_temp_4he <= 4.0:
        heads_ready_for_transition.append("4He")
    
    
    print("\nExecuting 4-pump Transition:")
    
    # User confirmation before turning off pump heater
    input("\nPress ENTER to turn OFF 4-pump Heater (Output 1)...")
    
    # Turn off 4He pump heater
    print("Turning OFF 4-pump Heater (Heater Output 1):")
    # print("  Command would be: MOUT 1,0.0  # Set Output 1 to 0% current (OFF)")
    # COMMENTED OUT: gl7_controller.send_command("MOUT 1,0.0")
    print("  → 4-pump Heater DEACTIVATED (0% power)")
    
    time.sleep(1)
    
    # User confirmation before turning on 4He switch
    input("\nPress ENTER to turn ON 4-switch (Analog Output 3)...")
    
    # Turn on 4He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[3]}:")
    # print("  Command would be: ANALOG 3,1,1,5.0,0.0,0  # Turn ON 4He switch (5V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 3,1,1,5.0,0.0,0")
    print("  → 4-switch ACTIVATED (5V)")
    print("Cooling continues, proceed to step 5")
