#!/usr/bin/env python3
"""
GL7 Step 4: 4He Pump Transition
"""

import time
from ...head3_calibration import convert_3head_resistance_to_temperature
from ...head4_calibration import convert_4head_resistance_to_temperature

def execute_step4_test(gl7_controller):
    """Execute GL7 Step 4: 4He Pump Transition"""
    print("GL7 STEP 4: 4-PUMP Heater TRANSITION")
    print("-" * 35)
    
    # Pre-transition temperature verification
    print("Temperature Check:")
    
    # Check head temperatures
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
    
    # Check stage temperatures
    pre_4k_stage = gl7_controller.read_temperature('D2')   # 4K stage (Input D2)
    pre_50k_stage = gl7_controller.read_temperature('D3')  # 50K stage (Input D3)
    print(f"  4K Stage Temperature (Channel 2 (D2)): {pre_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3 (D3)): {pre_50k_stage} K")
    
    # 3-pump temperature - read temperature directly (Input D)
    pre_temp_3pump = gl7_controller.read_temperature('D')
    
    # Check if we got a valid temperature reading
    if isinstance(pre_temp_3pump, float) and pre_temp_3pump > 0:
        print(f"  3-pump Temperature (Input D): {pre_temp_3pump:.3f} K")
    else:
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    # 4-pump temperature - read temperature directly from channel 5
    temp_4pump_response = gl7_controller.send_command("KRDG? 5")
    
    try:
        if temp_4pump_response and temp_4pump_response != "T_OVER":
            pre_temp_4pump = float(temp_4pump_response)
            print(f"  4-pump Temperature (Channel 5): {pre_temp_4pump:.3f} K")
        else:
            pre_temp_4pump = None
            print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    except ValueError:
        pre_temp_4pump = None
        print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    
    # Check heads for transition (for logic only)
    heads_ready_for_transition = []
    if isinstance(temp_3he_head, float) and temp_3he_head <= 4.0:
        heads_ready_for_transition.append("3He")
    if isinstance(temp_4he_head, float) and temp_4he_head <= 4.0:
        heads_ready_for_transition.append("4He")
    
    
    print("\nExecuting 4-pump Transition:")
    
    # User confirmation before turning off pump heater
    input("\nPress ENTER to turn OFF 4-pump Heater (Output 1)...")
    
    # Turn off 4He pump heater
    print("Turning OFF 4-pump Heater (Heater Output 1):")
    # print("  Command would be: MOUT 1,0.0  # Set Output 1 to 0% current (OFF)")
    # COMMENTED OUT: gl7_controller.send_command("MOUT 1,0.0")
    print("  → 4-pump Heater DEACTIVATED (0% power) (TEST MODE - command not executed)")
    
    time.sleep(1)
    
    # User confirmation before turning on 4He switch
    input("\nPress ENTER to turn ON 4-switch (Analog Output 3)...")
    
    # Turn on 4He heat switch
    print(f"Turning ON {gl7_controller.analog_heat_switches[3]}: (TEST MODE - command not executed)")
    # print("  Command would be: ANALOG 3,1,1,5.0,0.0,0  # Turn ON 4He switch (5V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 3,1,1,5.0,0.0,0")
    print("  → 4-switch ACTIVATED (5V)")
    print("Cooling continues, proceed to step 5")
    
    return True
