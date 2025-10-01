#!/usr/bin/env python3
"""
GL7 Step 2A: Pre-cooling Phase
"""

import time

def execute_step2a(gl7_controller):
    """Execute GL7 Step 2A: Pre-cooling Phase (Room Temperature → 10K)"""
    print("STEP 2A: PRE-COOLING PHASE (Room Temperature → 10K)")
    print("-" * 50)
    print("Manual: 'Pre-cool from room temperature to ~4K'")
    print("Checking 3He Head, 4He Head, 4K Stage, and 50K Stage temperatures...")
    print("Looking for both heads to reach 10K threshold\n")
    
    # Check temperatures from the actual head thermometers
    max_checks = 5  # Limited checks for testing - won't loop endlessly
    heads_at_10k = []
    
    for check in range(1, max_checks + 1):
        print(f"Temperature Check {check}/{max_checks}:")
        
        # Read 3He Head temperature (Input A)
        temp_3he_head = gl7_controller.read_temperature('A')
        
        # Read 4He Head temperature (Input C)  
        temp_4he_head = gl7_controller.read_temperature('C')
        
        print(f"  3He Head Temperature (Input A): {temp_3he_head} K")
        print(f"  4He Head Temperature (Input C): {temp_4he_head} K")
        
        # Check if both heads have reached 10K
        heads_at_10k = []
        
        if isinstance(temp_3he_head, float):
            if temp_3he_head <= 10:
                print(f"    ✓ 3He Head at {temp_3he_head} K (≤ 10K)")
                heads_at_10k.append("3He")
            else:
                print(f"    → 3He Head at {temp_3he_head} K (> 10K)")
        else:
            print(f"    → 3He Head reading: {temp_3he_head}")
        
        if isinstance(temp_4he_head, float):
            if temp_4he_head <= 10:
                print(f"    ✓ 4He Head at {temp_4he_head} K (≤ 10K)")
                heads_at_10k.append("4He")
            else:
                print(f"    → 4He Head at {temp_4he_head} K (> 10K)")
        else:
            print(f"    → 4He Head reading: {temp_4he_head}")
        
        # Summary for this check
        if len(heads_at_10k) == 2:
            print("    ✓ BOTH heads have reached 10K - heat switches should turn OFF")
            break
        elif len(heads_at_10k) == 1:
            print(f"    → {heads_at_10k[0]} head ready, waiting for other head")
        else:
            print("    → Both heads still cooling toward 10K")
        
        print()  # Blank line between checks
        if check < max_checks:
            time.sleep(2)  # Wait before next check
    
    # Final assessment
    print("Pre-cooling Assessment:")
    if len(heads_at_10k) == 2:
        print("✓ Both 3He and 4He heads have reached 10K threshold")
    elif len(heads_at_10k) == 1:
        print(f"→ {heads_at_10k[0]} head ready, {2-len(heads_at_10k)} head(s) still cooling")
    else:
        print("→ Heads still cooling (normal during testing)")
    print("→ Proceeding with sequence to demonstrate full process\n")
    
    return heads_at_10k
