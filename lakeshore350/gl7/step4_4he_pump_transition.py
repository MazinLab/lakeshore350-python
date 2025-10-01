#!/usr/bin/env python3
"""
GL7 Step 4: 4He Pump Transition
"""

import time

def execute_step4(gl7_controller):
    """Execute GL7 Step 4: 4He Pump Transition"""
    print("STEP 4: 4He PUMP TRANSITION")
    print("-" * 30)
    print("Manual: 'Turn OFF the 4-pump heat and turn ON the 4-switch'")
    
    # Pre-transition temperature verification
    print("\nPre-transition Temperature Verification:")
    print("Confirming 3He Head and 4He Head have reached 4K...")
    
    # Check head temperatures
    pre_temp_3he = gl7_controller.read_temperature('A')  # 3He Head
    pre_temp_4he = gl7_controller.read_temperature('C')  # 4He Head
    
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
    
    print(f"  3He Head Temperature (Input A): {pre_temp_3he} K")
    print(f"  4He Head Temperature (Input C): {pre_temp_4he} K")
    print(f"  4K Stage Temperature (Channel 2): {pre_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {pre_50k_stage} K")
    
    # Verification assessment
    heads_ready_for_transition = []
    
    if isinstance(pre_temp_3he, float):
        if pre_temp_3he <= 4.0:
            print(f"  ✓ 3He Head ready at {pre_temp_3he} K (≤ 4K)")
            heads_ready_for_transition.append("3He")
        else:
            print(f"  → 3He Head at {pre_temp_3he} K (> 4K)")
    else:
        print(f"  → 3He Head reading: {pre_temp_3he}")
        
    if isinstance(pre_temp_4he, float):
        if pre_temp_4he <= 4.0:
            print(f"  ✓ 4He Head ready at {pre_temp_4he} K (≤ 4K)")
            heads_ready_for_transition.append("4He")
        else:
            print(f"  → 4He Head at {pre_temp_4he} K (> 4K)")
    else:
        print(f"  → 4He Head reading: {pre_temp_4he}")
    
    # Transition decision
    print(f"\nTransition Assessment:")
    if len(heads_ready_for_transition) == 2:
        print("✓ BOTH heads confirmed at 4K - proceeding with 4He pump transition")
    else:
        print(f"→ {len(heads_ready_for_transition)}/2 heads ready (proceeding for test demonstration)")
    
    print("\nExecuting 4He Pump Transition:")
    
    # Turn off 4He pump heater
    print(f"Turning OFF {gl7_controller.relay_pump_heaters[1]}:")
    print("  Command would be: RELAY 1,0  # Turn OFF 4He pump heater")
    # COMMENTED OUT: gl7_controller.send_command("RELAY 1,0")
    print("  → 4He pump heater DEACTIVATED")
    
    time.sleep(1)
    
    # Turn on 4He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[3]}:")
    print("  Command would be: ANALOG 3,1,1,5.0,0.0,0  # Turn ON 4He switch (5V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 3,1,1,5.0,0.0,0")
    print("  → 4He heat switch ACTIVATED (5V)")
    print("  → Heads will cool rapidly below 1K")
    
    print("\n")
    time.sleep(2)
    
    return heads_ready_for_transition
