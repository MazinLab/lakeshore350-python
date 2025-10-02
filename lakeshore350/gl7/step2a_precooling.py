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
    
    print(f"  3-head Temperature (Input A): {temp_3he_head} K")
    print(f"  4-head Temperature (Input C): {temp_4he_head} K")
    
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
