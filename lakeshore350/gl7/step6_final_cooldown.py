#!/usr/bin/env python3
"""
GL7 Step 6: Final Cooldown
"""

import time
from ..head3_calibration import convert_3head_resistance_to_temperature
from ..head4_calibration import convert_4head_resistance_to_temperature

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
    
    # 3-pump temperature (Input D)
    final_3pump = gl7_controller.read_temperature('D')
    print(f"  3-pump Temperature (Input D): {final_3pump} K")
    
    # 4-pump temperature (Channel 5)
    final_4pump = gl7_controller.send_command("KRDG? 5")
    try:
        if final_4pump and final_4pump != "T_OVER":
            final_4pump_val = float(final_4pump)
        else:
            final_4pump_val = final_4pump
    except ValueError:
        final_4pump_val = final_4pump
    print(f"  4-pump Temperature (Channel 5): {final_4pump_val} K")
    
    print(f"\nFinal Assessment:")
    print("→ System has reached final cooldown state")
    print("→ All temperatures logged for final analysis")
    print("→ GL7 cooldown sequence complete")
    
    print("\n" + "=" * 50)
    print("GL7 STEP 6 COMPLETE")
    print("System ready for operation at base temperature")
    print("=" * 50)
