#!/usr/bin/env python3
"""
GL7 Step 2B: Heat Switch Status Verification
"""

import time

def execute_step2b(gl7_controller):
    """Execute GL7 Step 2B: Heat Switch Status Verification"""
    print("STEP 2B: HEAT SWITCH STATUS VERIFICATION")
    print("-" * 40)
    print("Manual: 'During pre-cooling, when both heat switches turn OFF (< 10K)'")
    print("Verifying that both heat switches have turned OFF...")
    print("Checking 3He Head, 4He Head, 4K Stage, and 50K Stage temperatures...")
    
    # Check analog heat switch status
    print("\nChecking heat switch status:")
    for output_num, name in gl7_controller.analog_heat_switches.items():
        config = gl7_controller.query_analog_status(output_num)
        print(f"  {name} (Analog {output_num}): {config}")
    
    # Verify head temperatures are at 10K threshold
    print("\nChecking head thermometer readings:")
    
    # 3He Head thermometer (Input A)
    temp_3he_head = gl7_controller.read_temperature('A')
    print(f"  3He Head Temperature (Input A): {temp_3he_head} K")
    
    # 4He Head thermometer (Input C)
    temp_4he_head = gl7_controller.read_temperature('C')
    print(f"  4He Head Temperature (Input C): {temp_4he_head} K")
    
    # Also check 4K and 50K stage temperatures
    print("\nChecking stage temperatures:")
    
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
    
    # Temperature assessment
    print("\nTemperature Assessment:")
    head_temps_ready = []
    
    if isinstance(temp_3he_head, float) and temp_3he_head <= 10:
        print(f"  ✓ 3He Head ready at {temp_3he_head} K (≤ 10K)")
        head_temps_ready.append("3He")
    elif isinstance(temp_3he_head, float):
        print(f"  → 3He Head at {temp_3he_head} K (> 10K)")
    else:
        print(f"  → 3He Head reading: {temp_3he_head}")
        
    if isinstance(temp_4he_head, float) and temp_4he_head <= 10:
        print(f"  ✓ 4He Head ready at {temp_4he_head} K (≤ 10K)")
        head_temps_ready.append("4He")
    elif isinstance(temp_4he_head, float):
        print(f"  → 4He Head at {temp_4he_head} K (> 10K)")
    else:
        print(f"  → 4He Head reading: {temp_4he_head}")
    
    if len(head_temps_ready) == 2:
        print("  ✓ Both heads at 10K threshold - heat switches should be OFF")
        print("  → Ready to proceed to pump heating phase")
    else:
        print(f"  → {len(head_temps_ready)}/2 heads ready for pump heating")
    
    print("\n")
    
    return head_temps_ready
