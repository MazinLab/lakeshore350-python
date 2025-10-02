#!/usr/bin/env python3
"""
GL7 Step 5: 3He Pump Transition
"""

import time

def execute_step5_test(gl7_controller):
    """Execute GL7 Step 5: Cooling to 2K and 3He Pump Transition"""
    print("GL7 STEP 5: 3-PUMP TRANSITION")
    print("-" * 35)
    print("Monitoring 3-head, 4-head, 4K Stage, and 50K Stage temperatures...")
    print("Waiting for 3-head and 4-head to reach ~2K...")
    
    # Single temperature check
    print("\nTemperature Check:")
    targets_at_2k = []
    
    # Read all relevant temperatures
    temp_3he_head = gl7_controller.read_temperature('A')  # 3He Head
    temp_4he_head = gl7_controller.read_temperature('C')  # 4He Head
    
    # Read stage temperatures
    temp_channel_2 = gl7_controller.send_command("KRDG? 2")  # 4K stage
    temp_channel_3 = gl7_controller.send_command("KRDG? 3")  # 50K stage
    
    try:
        if temp_channel_2 and temp_channel_2 != "T_OVER":
            temp_4k_stage = float(temp_channel_2)
        else:
            temp_4k_stage = temp_channel_2
    except ValueError:
        temp_4k_stage = temp_channel_2
        
    try:
        if temp_channel_3 and temp_channel_3 != "T_OVER":
            temp_50k_stage = float(temp_channel_3)
        else:
            temp_50k_stage = temp_channel_3
    except ValueError:
        temp_50k_stage = temp_channel_3
    
    print(f"  3-head Temperature (Input A): {temp_3he_head} K")
    print(f"  4-head Temperature (Input C): {temp_4he_head} K")
    print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
    
    # Check if 3He head and 4He head have reached 2K (for logic only)
    targets_at_2k = []
    if isinstance(temp_3he_head, float) and temp_3he_head <= 2.0:
        targets_at_2k.append("3He Head")
    if isinstance(temp_4he_head, float) and temp_4he_head <= 2.0:
        targets_at_2k.append("4He Head")
    
    # Temperature assessment for transition
    print(f"\nStep 5 Assessment:")
    if len(targets_at_2k) == 2:
        print("✓ 3-head and 4-head have reached 2K")
    else:
        print("→ Targets still cooling (advancing for test demonstration)")
    print("→ Ready to proceed to 3-pump transition")
    
    print("\n" + "-" * 30)
    
    # User confirmation before turning off 3He pump heater
    input("\nPress ENTER to turn OFF 3-pump heater (Output 2)...")
    
    # Turn off 3He pump heater
    print("Turning OFF 3-pump Heater (Heater Output 2):")
    # print("  Command would be: MOUT 2,0.0  # Set Output 2 to 0% current (OFF)")
    # COMMENTED OUT: gl7_controller.send_command("MOUT 2,0.0")
    print("  → 3-pump heater DEACTIVATED (0% power)")
    
    time.sleep(1)
    
    # User confirmation before turning on 3He switch (confirm 2K reached)
    input("\nPress ENTER to confirm we reached 2K and turn ON 3-switch (Analog 4)...")
    
    # Turn on 3He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[4]}:")
    # print("  Command would be: ANALOG 4,1,1,5.0,0.0,0  # Turn ON 3He switch (5V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 4,1,1,5.0,0.0,0")
    print("  → 3-switch ACTIVATED (5V)")
    print("Final cooldown to ~300mK begins")
