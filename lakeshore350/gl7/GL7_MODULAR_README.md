# GL7 Modular Control System

## Overview

The GL7 operating procedure is broken up into 8 different scripts, or steps. These are intended to be ran automatically but can be ran individually for troubleshooting.

## Current Directory Structure

```
lakeshore350/
├── gl7_control.py          # Main GL7 controller class
└── gl7/                     
    ├── __init__.py         
    ├── step1_initial_status.py
    ├── step2a_precooling.py
    ├── step2b_heat_switch_verification.py
    ├── step3_pump_heating.py
    ├── step4_4he_pump_transition.py
    ├── step5_cooling_to_2k.py
    ├── step6_3he_pump_transition.py
    ├── step7_final_cooldown.py
    └── step8_final_status.py
```

## Usage

### Complete GL7 Sequence (Unchanged)
```bash
lakeshore350 --start-gl7-test
```
Automatically runs complete GL7 operation sequence

### Individual Step Execution (New)
```bash
# Execute individual steps manually
lakeshore350 --gl7-step1     # Initial status check
lakeshore350 --gl7-step2a    # Pre-cooling phase to 10K 
lakeshore350 --gl7-step2b    # Verifying both heat switches are off
lakeshore350 --gl7-step3     # Start pump heaters, confirm pump temperature > 25 K
lakeshore350 --gl7-step4     # Confirm pumps ~ 4K, turn off 4 pump heater, turn on 4 switch
lakeshore350 --gl7-step5     # Confirm pumps ~ 2K 
lakeshore350 --gl7-step6     # 3He Pump Transition
lakeshore350 --gl7-step7     # Final Cooldown Monitoring
lakeshore350 --gl7-step8     # Final Status Check, turn of 4 pump heater, turn on 
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

### Step 5: Cooling to 2K
- Monitors all temperature points
- Waits for 3He Head and 4K Stage to reach 2K
- Returns list of targets that have reached 2K

### Step 6: 3He Pump Transition
- Turns OFF 3He pump heater
- Turns ON 3He heat switch
- Initiates final cooldown phase

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

## Backward Compatibility

The complete GL7 sequence (`--start-gl7-test`) produces **identical output** to the previous version. The modular approach is completely transparent when using the full sequence command.
