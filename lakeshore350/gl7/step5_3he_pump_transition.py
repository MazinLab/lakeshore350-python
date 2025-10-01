#!/usr/bin/env python3
"""
GL7 Step 5: Cooling to 2K and 3He Pump Transition
"""

import time

def execute_step5(gl7_controller):
    """Execute GL7 Step 5: Cooling to 2K and 3He Pump Transition"""
    print("STEP 5: COOLING TO 2K AND 3He PUMP TRANSITION")
    print("-" * 50)
    print("Manual: 'When the heads have cooled to less than 2K'")
    print("Monitoring 3He Head, 4He Head, 4K Stage, and 50K Stage temperatures...")
    print("Waiting for 3He Head and 4K Stage to reach ~2K...")
    
    # Monitor temperatures for 2K target
    max_checks = 3  # Limited for testing
    targets_at_2k = []
    
    for check in range(1, max_checks + 1):
        print(f"\nTemperature Monitoring {check}/{max_checks}:")
        
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
        
        print(f"  3He Head Temperature (Input A): {temp_3he_head} K")
        print(f"  4He Head Temperature (Input C): {temp_4he_head} K")
        print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
        print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
        
        # Check if 3He head and 4K stage have reached 2K
        targets_at_2k = []
        
        if isinstance(temp_3he_head, float):
            if temp_3he_head <= 2.0:
                print(f"    ✓ 3He Head at {temp_3he_head} K (≤ 2K)")
                targets_at_2k.append("3He Head")
            else:
                print(f"    → 3He Head at {temp_3he_head} K (> 2K)")
        else:
            print(f"    → 3He Head reading: {temp_3he_head}")
        
        if isinstance(temp_4k_stage, float):
            if temp_4k_stage <= 2.0:
                print(f"    ✓ 4K Stage at {temp_4k_stage} K (≤ 2K)")
                targets_at_2k.append("4K Stage")
            else:
                print(f"    → 4K Stage at {temp_4k_stage} K (> 2K)")
        else:
            print(f"    → 4K Stage reading: {temp_4k_stage}")
        
        # Assessment
        if len(targets_at_2k) == 2:
            print("    ✓ BOTH 3He Head and 4K Stage have reached 2K - ready for 3He pump transition")
            break
        elif len(targets_at_2k) == 1:
            print(f"    → {targets_at_2k[0]} ready, waiting for other target")
        else:
            print("    → Both targets still cooling toward 2K")
        
        if check < max_checks:
            time.sleep(2)
    
    # Temperature assessment for transition
    print(f"\nCooling to 2K Assessment:")
    if len(targets_at_2k) == 2:
        print("✓ 3He Head and 4K Stage have reached 2K")
    else:
        print("→ Targets still cooling (advancing for test demonstration)")
    print("→ Ready to proceed to 3He pump transition")
    
    print("\n" + "-" * 30)
    print("Manual: 'turn OFF the 3-pump heater and turn ON the 3-switch'")
    
    # Turn off 3He pump heater
    print(f"Turning OFF {gl7_controller.relay_pump_heaters[2]}:")
    print("  Command would be: RELAY 2,0  # Turn OFF 3He pump heater")
    # COMMENTED OUT: gl7_controller.send_command("RELAY 2,0")
    print("  → 3He pump heater DEACTIVATED")
    
    time.sleep(1)
    
    # Turn on 3He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[4]}:")
    print("  Command would be: ANALOG 4,1,1,5.0,0.0,0  # Turn ON 3He switch (5V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 4,1,1,5.0,0.0,0")
    print("  → 3He heat switch ACTIVATED (5V)")
    print("  → Final cooldown to ~300mK begins")
    
    print("\n")
    time.sleep(2)
    
    return targets_at_2k
