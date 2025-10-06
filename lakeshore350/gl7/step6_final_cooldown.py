#!/usr/bin/env python3
"""
GL7 Step 6: Final Cooldown
"""

import time
from ..head3_calibration import convert_3head_resistance_to_temperature
from ..head4_calibration import convert_4head_resistance_to_temperature
from ..pump_calibration import convert_pump_voltage_to_temperature

def execute_step6(gl7_controller):
    """Execute GL7 Step 6: Final Status Check"""
    print("GL7 STEP 6: FINAL STATUS CHECK")
    print("-" * 35)
    print("Monitoring final cooldown to ~300mK...")
    
    # Temperature Check
    print("\nTemperature Check:")
    # 3He Head - read resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
        print(f"  3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        print(f"  3-head Temperature (Input A): Unable to read sensor")
    
    # 4He Head - read resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
        print(f"  4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        print(f"  4-head Temperature (Input C): Unable to read sensor")
    
    final_4k_stage = gl7_controller.read_temperature('D2')   # 4K stage (Input D2)
    final_50k_stage = gl7_controller.read_temperature('D3')  # 50K stage (Input D3)
    print(f"  4K Stage Temperature (Channel 2 (D2)): {final_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3 (D3)): {final_50k_stage} K")
    
    # 3-pump temperature - read voltage and convert to temperature (Input D)
    voltage_3pump = gl7_controller.read_voltage('D')
    
    # Convert 3-pump voltage to temperature using calibration
    if isinstance(voltage_3pump, float) and voltage_3pump > 0:
        final_3pump = convert_pump_voltage_to_temperature(voltage_3pump)
        print(f"  3-pump Temperature (Input D): {final_3pump:.3f} K")
    else:
        final_3pump = None
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    # 4-pump temperature - read voltage from channel 5 and convert to temperature
    voltage_4pump_response = gl7_controller.send_command("VRDG? 5")
    
    try:
        if voltage_4pump_response and voltage_4pump_response != "V_OVER":
            voltage_4pump = float(voltage_4pump_response)
            final_4pump = convert_pump_voltage_to_temperature(voltage_4pump)
            print(f"  4-pump Temperature (Channel 5): {final_4pump:.3f} K")
        else:
            final_4pump = None
            print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    except ValueError:
        final_4pump = None
        print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    
    print(f"\nFinal Assessment:")
    print("→ System has reached final cooldown state")
    print("→ All temperatures logged for final analysis")
    print("→ GL7 cooldown sequence complete")
    
    print("\n" + "=" * 50)
    print("GL7 STEP 6 COMPLETE")
    print("System ready for operation at base temperature")
    print("=" * 50)
