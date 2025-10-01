# GL7 Modular Control System

## Overview

The GL7 Sorption Cooler control system has been modularized into 7 individual step scripts while maintaining the exact same functionality when running the complete sequence with `--start-gl7-test`.

## Directory Structure

```
lakeshore350/
├── gl7_control.py          # Main GL7 controller class (unchanged interface)
└── gl7/                    # New modular step directory
    ├── __init__.py         # Module initialization
    ├── step1_initial_status.py
    ├── step2a_precooling.py
    ├── step2b_heat_switch_verification.py
    ├── step3_pump_heating.py
    ├── step4_4he_pump_transition.py
    ├── step6_3he_pump_transition.py    # Combined cooling + transition
    ├── step7_final_cooldown.py
    └── step8_final_status.py
```

## Usage

### Complete GL7 Sequence (Unchanged)
```bash
lakeshore350 --start-gl7-test
```
This runs the complete 7-step GL7 sequence exactly as before.

### Individual Step Execution (New)
```bash
# Execute individual steps manually
lakeshore350 --gl7-step1     # Initial Status Check
lakeshore350 --gl7-step2a    # Pre-cooling Phase
lakeshore350 --gl7-step2b    # Heat Switch Status Verification
lakeshore350 --gl7-step3     # Pump Heating Phase
lakeshore350 --gl7-step4     # 4He Pump Transition
lakeshore350 --gl7-step6     # Cooling to 2K and 3He Pump Transition
lakeshore350 --gl7-step7     # Final Cooldown Monitoring
lakeshore350 --gl7-step8     # Final Status Check
```

## Step Details

### Step 1: Initial Status Check
- Reads all temperature measurement points
- Checks current heater/switch status
- Provides baseline system state

### Step 2A: Pre-cooling Phase
- Monitors 3He Head, 4He Head, 4K Stage, and 50K Stage temperatures
- Waits for both heads to reach 10K threshold
- Returns list of heads that have reached 10K

### Step 2B: Heat Switch Status Verification
- Verifies heat switches have turned OFF at 10K
- Checks all temperature points and switch status
- Confirms readiness for pump heating

### Step 3: Pump Heating Phase
- Activates both pump heaters to 45-55K (simulation mode)
- Monitors all temperature points
- Waits for heads to reach 4K
- Includes final temperature confirmation

### Step 4: 4He Pump Transition
- Pre-transition temperature verification
- Turns OFF 4He pump heater
- Turns ON 4He heat switch
- Confirms both heads are at 4K before transition

### Step 6: Cooling to 2K and 3He Pump Transition (Combined)
- **Part 1 - Temperature Monitoring**: Monitors all temperature points and waits for 3He Head and 4K Stage to reach 2K
- **Part 2 - 3He Pump Transition**: Turns OFF 3He pump heater and turns ON 3He heat switch
- Initiates final cooldown phase
- Returns list of targets that have reached 2K

### Step 7: Final Cooldown Monitoring
- Monitors approach to 300mK target
- Checks all temperature points
- Returns final 4He Head temperature

### Step 8: Final Status Check
- Final temperature readings from all points
- Checks if GL7 is running (4He Head ≤ 300mK)
- Shows final heater/switch status
- Returns GL7 running status

## Temperature Monitoring Points

Each step monitors the key GL7 measurement points:
- **3He Head Temperature** (Input A)
- **4He Head Temperature** (Input C)  
- **4K Stage Temperature** (Channel 2)
- **50K Stage Temperature** (Channel 3)
- **Device Stage Temperature** (Input B)

## Safety Features

- All heater commands remain commented out for safety
- Each step can be aborted with Ctrl+C
- Steps return status information for verification
- Simulation mode shows exact commands that would be executed

## Benefits

1. **Manual Control**: Each step can be run individually for troubleshooting
2. **Debugging**: Isolate specific phases of the GL7 sequence
3. **Testing**: Verify individual step functionality
4. **Flexibility**: Run partial sequences as needed
5. **Maintenance**: Unchanged `--start-gl7-test` preserves existing workflow
6. **Streamlined Process**: Combined Step 6 reduces redundant temperature checks

## Recent Changes

- **Step 5 Removed**: The separate "Cooling to 2K" step has been eliminated
- **Step 6 Enhanced**: Now combines temperature monitoring (cooling to 2K) with the 3He pump transition
- **Sequence Shortened**: 7 steps instead of 8, reducing complexity while maintaining full functionality
- **Better Flow**: More logical progression from 4He transition directly to combined 2K cooling + 3He transition

## Backward Compatibility

The complete GL7 sequence (`--start-gl7-test`) produces **identical output** to the previous version. The modular approach is completely transparent when using the full sequence command.
