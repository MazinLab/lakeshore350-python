#!/usr/bin/env python3
"""
GL7 Step 2A: Pre-cooling Phase
"""

import time

def execute_step2a(gl7_controller):
    """Execute GL7 Step 2a: Pre-cooling from room temperature to ~4K"""
    print("GL7 STEP 2A: PRE-COOLING PHASE")
    print("-" * 35)
    print("Before turning on the pulse tube, ensure GL7 heat switches are ON\n")
    
    # Manual heat switch control - Turn switches ON before ADR
    print("Manual Heat Switch Control:")
    input("Press ENTER to turn ON 4-switch...")
    print("  → Turning ON 4-switch (Analog 3 to 5V)")
    gl7_controller.send_command("ANALOG 3,1,1,5.0,0.0,0")
    
    input("Press ENTER to turn ON 3-switch...")
    print("  → Turning ON 3-switch (Analog 4 to 5V)")
    gl7_controller.send_command("ANALOG 4,1,1,5.0,0.0,0")
    print()
    
    # Single temperature check - operator will confirm readiness in Step 2b
    print("Temperature Check:")
    heads_at_10k = []
    
    # Read 3He Head temperature (Input A)
    temp_3he_head = gl7_controller.read_temperature('A')
    
    # Read 4He Head temperature (Input C)  
    temp_4he_head = gl7_controller.read_temperature('C')
    
    # 4K stage temperature (Input D2)
    temp_4k_stage = gl7_controller.read_temperature('D2')
    
    # 50K stage temperature (Input D3)
    temp_50k_stage = gl7_controller.read_temperature('D3')
    
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
    print(f"  4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    print(f"  3-pump Temperature (Input D): {temp_3pump} K")
    print(f"  4-pump Temperature (Channel 5): {temp_4pump_val} K")
    
    print()
    print("→ Start pulse tube cooling and proceed to next step")
