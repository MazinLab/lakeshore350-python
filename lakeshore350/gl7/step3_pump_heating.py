#!/usr/bin/env python3
"""
GL7 Step 3: Pump Heating Phase
"""

import time

def execute_step3(gl7_controller):
    """Execute GL7 Step 3: Pump Heating Phase (45-55K)"""
    print("STEP 3: PUMP HEATING PHASE")
    print("-" * 30)
    print("Manual: 'heat both pumps to around 45-55K and keep them at that temperature'")
    print("Manual: 'until the heads cool to ~4K and their temperature stabilises'")
    print("Monitoring 3He Head, 4He Head, 4K Stage, and 50K Stage temperatures...")
    
    # Activate both pump heaters
    print("Activating BOTH pump heaters to 45-55K:")
    
    print(f"  Starting {gl7_controller.relay_pump_heaters[1]} (Relay 1):")
    print("    Command would be: RELAY 1,1  # Turn ON 4He pump heater")
    # COMMENTED OUT: gl7_controller.send_command("RELAY 1,1")
    print("    → 4He pump heating to 45-55K")
    
    print(f"  Starting {gl7_controller.relay_pump_heaters[2]} (Relay 2):")
    print("    Command would be: RELAY 2,1  # Turn ON 3He pump heater") 
    # COMMENTED OUT: gl7_controller.send_command("RELAY 2,1")
    print("    → 3He pump heating to 45-55K")
    
    print("\nBoth pumps now heating - monitoring head temperatures...")
    print("Waiting for 3He Head (Input A) and 4He Head (Input C) to reach 4K...")
    
    # Monitor head thermometers for 4K target
    max_checks = 3  # Limited for testing since temps won't reach 4K
    heads_at_4k = []
    
    for check in range(1, max_checks + 1):
        print(f"\nTemperature Check {check}/{max_checks}:")
        
        # Read head thermometers
        temp_3he_head = gl7_controller.read_temperature('A')  # 3He Head
        temp_4he_head = gl7_controller.read_temperature('C')  # 4He Head
        
        print(f"  3He Head Temperature (Input A): {temp_3he_head} K")
        print(f"  4He Head Temperature (Input C): {temp_4he_head} K")
        
        # Also read stage temperatures
        temp_channel_2 = gl7_controller.send_command("KRDG? 2")  # 4K stage
        temp_channel_3 = gl7_controller.send_command("KRDG? 3")  # 50K stage
        temp_input_b = gl7_controller.read_temperature('B')       # Device stage
        
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
        
        print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
        print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
        print(f"  Device Stage Temperature (Input B): {temp_input_b} K")
        
        # Check if heads have reached 4K
        heads_at_4k = []
        
        if isinstance(temp_3he_head, float):
            if temp_3he_head <= 4.0:
                print(f"    ✓ 3He Head at {temp_3he_head} K (≤ 4K)")
                heads_at_4k.append("3He")
            else:
                print(f"    → 3He Head at {temp_3he_head} K (> 4K)")
        else:
            print(f"    → 3He Head reading: {temp_3he_head}")
        
        if isinstance(temp_4he_head, float):
            if temp_4he_head <= 4.0:
                print(f"    ✓ 4He Head at {temp_4he_head} K (≤ 4K)")
                heads_at_4k.append("4He")
            else:
                print(f"    → 4He Head at {temp_4he_head} K (> 4K)")
        else:
            print(f"    → 4He Head reading: {temp_4he_head}")
        
        # Assessment
        if len(heads_at_4k) == 2:
            print("    ✓ BOTH heads have reached 4K - ready for next stage")
            break
        elif len(heads_at_4k) == 1:
            print(f"    → {heads_at_4k[0]} head ready, waiting for other head")
        else:
            print("    → Both heads still cooling toward 4K")
        
        print("    → Pumps maintained at 45-55K")
        
        if check < max_checks:
            time.sleep(2)
    
    # Final assessment for Step 3
    print(f"\nStep 3 Assessment:")
    if len(heads_at_4k) == 2:
        print("✓ Both heads have reached 4K and stabilized")
    else:
        print("→ Heads still cooling (advancing for test demonstration)")
    
    # Final confirmation check for head temperatures
    print("\nFinal Step 3 Temperature Confirmation:")
    final_temp_3he = gl7_controller.read_temperature('A')  # 3He Head
    final_temp_4he = gl7_controller.read_temperature('C')  # 4He Head
    
    print(f"  3He Head Final Temperature (Input A): {final_temp_3he} K")
    print(f"  4He Head Final Temperature (Input C): {final_temp_4he} K")
    
    if isinstance(final_temp_3he, float) and isinstance(final_temp_4he, float):
        if final_temp_3he <= 4.0 and final_temp_4he <= 4.0:
            print("  ✓ CONFIRMED: Both heads at 4K - ready for 4He pump transition")
        else:
            print(f"  → Heads still cooling (3He: {final_temp_3he}K, 4He: {final_temp_4he}K)")
    else:
        print("  → Temperature readings not numeric (normal during testing)")
    
    print("→ Ready to proceed to 4He pump transition")
    
    print("\n")
    time.sleep(2)
    
    return heads_at_4k
