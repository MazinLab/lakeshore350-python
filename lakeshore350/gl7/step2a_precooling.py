#!/usr/bin/env python3
"""
GL7 Step 2A: Pre-cooling Phase
"""

import time

def execute_step2a(gl7_controller):
    """Execute GL7 Step 2a: Pre-cooling from room temperature to ~4K"""
    print("GL7 STEP 2A: PRE-COOLING PHASE")
    print("-" * 35)
    print("ADR should be turned ON at this stage")
    print("Monitoring 3-head and 4-head as they cool to ~10K threshold...")
    print("This step takes no actions, it checks current temperatures and proceeds to Step 2b for user input.\n")
    
    # Single temperature check - operator will confirm readiness in Step 2b
    print("Temperature Check:")
    heads_at_10k = []
    
    # Read 3He Head temperature (Input A)
    temp_3he_head = gl7_controller.read_temperature('A')
    
    # Read 4He Head temperature (Input C)  
    temp_4he_head = gl7_controller.read_temperature('C')
    
    # 4K stage temperature (Channel 2)
    temp_channel_2 = gl7_controller.send_command("KRDG? 2")
    try:
        if temp_channel_2 and temp_channel_2 != "T_OVER":
            temp_4k_stage = float(temp_channel_2)
        else:
            temp_4k_stage = temp_channel_2
    except ValueError:
        temp_4k_stage = temp_channel_2
    
    # 50K stage temperature (Channel 3)
    temp_channel_3 = gl7_controller.send_command("KRDG? 3")
    try:
        if temp_channel_3 and temp_channel_3 != "T_OVER":
            temp_50k_stage = float(temp_channel_3)
        else:
            temp_50k_stage = temp_channel_3
    except ValueError:
        temp_50k_stage = temp_channel_3
    
    # 3-pump temperature (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    # 4-pump temperature (Channel 5)
    temp_4pump = gl7_controller.send_command("KRDG? 5")
    try:
        if temp_4pump and temp_4pump != "T_OVER":
            temp_4pump_val = float(temp_4pump)
        else:
            temp_4pump_val = temp_4pump
    except ValueError:
        temp_4pump_val = temp_4pump

    print(f"  3-head Temperature (Input A): {temp_3he_head} K")
    print(f"  4-head Temperature (Input C): {temp_4he_head} K")
    print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
    print(f"  3-pump Temperature (Input D): {temp_3pump} K")
    print(f"  4-pump Temperature (Channel 5): {temp_4pump_val} K")
    
    # Check if both heads have reached 10K
    if isinstance(temp_3he_head, float):
        if temp_3he_head <= 10:
            print(f"    ✓ 3-head at {temp_3he_head} K (≤ 10K)")
            heads_at_10k.append("3He")
        else:
            print(f"    → 3-head at {temp_3he_head} K (> 10K)")
    else:
        print(f"    → 3-head reading: {temp_3he_head}")
    
    if isinstance(temp_4he_head, float):
        if temp_4he_head <= 10:
            print(f"    ✓ 4-head at {temp_4he_head} K (≤ 10K)")
            heads_at_10k.append("4He")
        else:
            print(f"    → 4-head at {temp_4he_head} K (> 10K)")
    else:
        print(f"    → 4-head reading: {temp_4he_head}")
    
    # Summary for this check
    if len(heads_at_10k) == 2:
        print("    ✓ BOTH heads have reached 10K - heat switches should turn OFF")
    elif len(heads_at_10k) == 1:
        print(f"    → {heads_at_10k[0]} head ready, waiting for other head")
    else:
        print("    → Both heads still cooling toward 10K")
    
    print()
    
    # Always proceed to Step 2b for user confirmation
    print("→ Proceeding to Step 2b for heat switch verification and user input")
