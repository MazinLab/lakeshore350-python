#!/usr/bin/env python3
"""
GL7 Step 5: 3He Pump Transition
"""

import time
from ...head3_calibration import convert_3head_resistance_to_temperature
from ...head4_calibration import convert_4head_resistance_to_temperature

def execute_step5_test(gl7_controller):
    """Execute GL7 Step 5: Cooling to 2K and 3He Pump Transition"""
    print("GL7 STEP 5: 3-PUMP TRANSITION")
    print("-" * 35)
    print("Monitoring 3-head, 4-head, 4K Stage, and 50K Stage temperatures...")
    print("Waiting for 3-head and 4-head to reach ~2K...")
    
    # Single temperature check
    print("\nTemperature Check:")
    targets_at_2k = []
    
    # Read all relevant temperatures and resistances
    # 3He Head - read resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
        print(f"  3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        temp_3he_head = None
        print(f"  3-head Temperature (Input A): Unable to read sensor")
    
    # 4He Head - read resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
        print(f"  4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        temp_4he_head = None
        print(f"  4-head Temperature (Input C): Unable to read sensor")
    
    # Read stage temperatures
    temp_4k_stage = gl7_controller.read_temperature('D2')   # 4K stage (Input D2)
    temp_50k_stage = gl7_controller.read_temperature('D3')  # 50K stage (Input D3)
    print(f"  4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    
    # 3-pump temperature - read temperature directly (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    
    # Check if we got a valid temperature reading
    if isinstance(temp_3pump, float) and temp_3pump > 0:
        print(f"  3-pump Temperature (Input D): {temp_3pump:.3f} K")
    else:
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    # 4-pump temperature - read temperature directly from channel 5
    temp_4pump = gl7_controller.read_temperature(5)
    
    if isinstance(temp_4pump, float):
        print(f"  4-pump Temperature (Channel 5): {temp_4pump:.3f} K")
    else:
        print(f"  4-pump Temperature (Channel 5): {temp_4pump}")
    
    # Check if heads have reached 2K using calibrated temperatures
    targets_at_2k = []
    if temp_3he_head is not None and temp_3he_head <= 2.0:
        targets_at_2k.append("3He Head")
    if temp_4he_head is not None and temp_4he_head <= 2.0:
        targets_at_2k.append("4He Head")
    
    # Temperature assessment for transition
    print(f"\nStep 5 Assessment:")
    if len(targets_at_2k) >= 1:
        if "3He Head" in targets_at_2k:
            print("✓ 3-head has reached 2K (calibrated temperature)")
        if "4He Head" in targets_at_2k:
            print("✓ 4-head has reached 2K (calibrated temperature)")
    else:
        print("→ Heads still cooling (advancing for test demonstration)")
    print("→ Ready to proceed to 3-pump transition")
    
    print("\n" + "-" * 30)
    
    # User confirmation before turning off 3He pump heater
    input("\nPress ENTER to turn OFF 3-pump heater (Output 2)...")
    
    # Import heater controller for centralized heater management
    from ...heaters import HeaterController
    heater_ctrl = HeaterController(gl7_controller)
    
    # Turn off 3He pump heater
    print("Turning OFF 3-pump Heater (Heater Output 2):")
    # TEST MODE: Show what would be executed through heater controller
    print("  TEST MODE: Would execute heater_ctrl.turn_off_heater(2)")
    print("  → 3-pump heater DEACTIVATED (0% power) (TEST MODE - command not executed)")
    
    time.sleep(1)
    
    # User confirmation before turning on 3He switch (confirm 2K reached)
    input("\nPress ENTER to confirm we reached 2K and turn ON 3-switch (Analog 4)...")
    
    # Turn on 3He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[4]}: (TEST MODE - command not executed)")
    # TEST MODE: Show what would be executed through switch controller
    print("  TEST MODE: Would execute switch_ctrl.turn_on_switch(4)")
    print("  → 3-switch ACTIVATED (5V)")
    print("Final cooldown to ~300mK begins")
    
    return True
