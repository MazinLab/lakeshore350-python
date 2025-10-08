#!/usr/bin/env python3
"""
GL7 Step 2A: Pre-cooling Phase
"""

import time
from ..head3_calibration import convert_3head_resistance_to_temperature
from ..head4_calibration import convert_4head_resistance_to_temperature

def execute_step2a(gl7_controller):
    """Execute GL7 Step 2a: Pre-cooling from room temperature to ~4K"""
    print("GL7 STEP 2A: PRE-COOLING PHASE")
    print("-" * 35)
    print("Before turning on the pulse tube, ensure GL7 heat switches are ON\n")
    
    # Import switch controller for centralized switch management
    from ..switches import SwitchController
    switch_ctrl = SwitchController(gl7_controller)
    
    # Manual heat switch control - Turn switches ON before ADR
    print("Manual Heat Switch Control:")
    input("Press ENTER to turn ON 4-switch...")
    switch_ctrl.turn_on_switch(3)  # 4-switch is on analog output 3
    
    input("Press ENTER to turn ON 3-switch...")
    switch_ctrl.turn_on_switch(4)  # 3-switch is on analog output 4
    print()
    
    # Single temperature check - operator will confirm readiness in Step 2b
    print("Temperature Check:")
    heads_at_10k = []
    
    # Read 3He Head resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    
    # Convert 3-head resistance to temperature using calibration
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
    else:
        temp_3he_head = None
    
    # Read 4He Head resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    
    # Convert 4-head resistance to temperature using calibration
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
    else:
        temp_4he_head = None
    
    # 4K stage temperature (Input D3)
    temp_4k_stage = gl7_controller.read_temperature('D3')
    
    # 50K stage temperature (Channel 2)
    temp_50k_stage = gl7_controller.read_temperature(2)
    
    # 3-pump temperature - read temperature directly (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    
    # 4-pump temperature - read temperature directly from channel 5
    temp_4pump = gl7_controller.read_temperature(5)

    if temp_3he_head is not None:
        print(f"  3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        print(f"  3-head Temperature (Input A): Unable to read sensor")
    
    if temp_4he_head is not None:
        print(f"  4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        print(f"  4-head Temperature (Input C): Unable to read sensor")
        
    print(f"  4K Stage Temperature (D3): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 2): {temp_50k_stage} K")
    
    if temp_3pump is not None:
        print(f"  3-pump Temperature (Input D): {temp_3pump:.3f} K")
    else:
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    if isinstance(temp_4pump, float):
        print(f"  4-pump Temperature (Channel 5): {temp_4pump:.3f} K")
    else:
        print(f"  4-pump Temperature (Channel 5): {temp_4pump}")
    
    print()
    print("→ Start pulse tube cooling and proceed to next step")
