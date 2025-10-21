# Lake Shore 350 Python Interface

Python interface for reading temperatures from the Lakeshore 350 Temperature Controller.

## Installation

Clone this repository and install:
```bash
git clone https://github.com/MazinLab/lakeshore350-python
python3 -m venv lakeshore350-env
source lakeshore350-env/bin/activate  
cd lakeshore350-python
pip install -e .
```

## Usage
This repo is intended to be functional through simple command line arguments without running any scripts individually. 
To see a comprehensive list of command line functionality, execute ```lakeshore350 --help```

### Basic Checks
Read all inputs (A-C, D1-D5)
```bash
lakeshore350 --all
```

Get device information:
```bash
lakeshore350 --info
```

## Recording Temperatures 
### Calibrating GL7 Temperatures
The MEC 4K and 50K thermometers are read out in sensor units and calibrated directly on the lakeshore. The GL7 thermometry must be calibrated in software currently.  


For example, to request a sensor reading from the 3-head, we use ```read_sensor``` from ```TemperatureReader``` in ```temperature.py```. Then we import ```from .head3_calibration import convert_3head_resistance_to_temperature```. This function connects to the 3-head calibration .csv file located in ```\gl7_calibrations```. There is a calibration .csv for the 3-head, 4-head, and pumps/switches. There are also python files for creating the calibration for the 3-head, 4-head, and pumps/switches. These python files create linear interpolations based on the data provided in the calibration csv's. They can be called upon by their function, i.e. ```convert_3head_resistance_to_temperature``` to quickly convert a sensor measurement to a temperature. 

***Note the 4head calibration has a fudge factor currently, needs to be addressed for a more exact measurement. 

### ```temperature.py```
This is the primary python script that queries temperatures and sensor readings for the lakeshore350. The functionality from ```temperature.py``` is implimented in the whole repo. For inputs that directly have temperature outputs (or are calibrated directly on the lakeshore) like the 4K plate, we use the ```read_temperature``` function. For outputs that are read in sensor units like the 3-head, 4-head, 3-pump, or 4-pump, we use the ```read_sensor``` function.  

This script also includes the ```send_command``` function which allows us to send serial commands directly to the lakeshore. ```temperature.py``` does not convert sensor units to temperature, this is performed within ```main.py``` or ```record_temps.py```. It simply defines the functions for querying these sensor readings, or temperature readings, and then the calibrations are handled wherever the temperature is requested like ```main.py``` or ```record_temps.py```. 
### ```record_temps.py```
```record_temps.py``` should be run in a tmux pane whenever the fridge is running. Running this script will automatically create a .csv with the date in the ```\temps``` folder. If the folder doesn't exist yet it will create it. If you run ```record_temps.py``` multiple times in one day, it will append a number to the end of each .csv to differentiate them. 

```record_temps.py``` uses the ```TemperatureReader``` class from ```lakeshore350/temperature.py```. It will query the temperatures from the lakeshore every 30 minutes and print them as command line output and in the .csv. Currently, ```record_temps.py``` records:  
1) date  
2) time  
3) 4K temperature  
4) 50K temperature  
5) 3-head resistance and temperature
6) 4-head resistance, adjusted resistanced, and temperature from adjusted resistance
7) 3-pump voltage and temperature  
8) 4-pump voltage and temperature  
## Heaters/Switches (Outputs 1-4)

### Basic Command Line Functionality
Heater Output 1 -> 4-pump heater  
Heater Output 2 -> 3-pump heater   
Analog Output 3 -> 4-pump switch (4-switch)   
Analog Output 4 -> 3-pump switch (3-switch)   

To query the heater status,   
```bash
lakeshore350 --outputs-query-all
```
Returns a list of queries for all outputs    



To set output parameters (i.e. max current, mode),  
```bash
lakeshore350 --outputs-set-params
```    

To set heater range,
```bash
lakeshore350 --outputs-set-range
```  

To set output percentage,  
```bash
lakeshore350 --outputs-set OUTPUT PERCENT
```

**Note, when setting output percentage, query the output parameters through ```HTRSET``` or ```ANALOG``` first.  
This percentage is based on the set max current (which differs from output 1/2) and set max voltage (differs from output 3/4) based on the specified units. 
Max current output 1 = 0.1A, max current output 2 = 0.33A based on the GL7 300 Ohm resistance.  
Setting this value too high can damage the heaters/lakeshore350**

### Using outputs-query 
```lakeshore350 --outputs-query-all``` or ```lakeshore350 --outputs-query <output number>``` are the primary means of quering the status of outputs.   

The outputs print with the following syntax: 

**```MOUT?```** prints the manual output percentage (should be 0 if everything is off, or the percent the user set with ```outputs-set```   
**```HTR?```** is only for outputs 1 and 2. It prints the manual output percentage, should match ```MOUT```.     
**```HTRSET?```** is only for outputs 1 and 2. It prints the output parameters as ```<htr resistance>,<max current>,<max user current>,<current/power>```   
**```OUTMODE?```** prints the mode, as ```<mode>, <input>, <power up enable>```. This should print 3,0,0 (open loop mode, no input, power up disabled).     
**```RANGE?```** prints a number 1-5 of the output range. 5 means we are using 100% of the output range, it should be set to 5. To set output range, execute ```lakeshore350 --outputs-set-range <output> <range number 1-5>```   
**```AOUT?```** is only for outputs 3 and 4. It prints the manual output percentage, which should match ```MOUT```. It's the analog equivalent of the ```HTR?``` command     
**```ANALOG```** is only for outputs 3 and 4. It prints in the syntax ```<input>,<units>,<high value>,<low value>,<polarity>```. It can be changed with ```outputs-set-params```     


### Using outputs-set-params
#### Serial Syntax 
Executing ```lakeshore350 --outputs-set-params``` will prompt the two following commands. The command line walks the user through the process of setting these commands, this is just some more detail.   

All of these serial commands are initialized in outputs.py and called to in main.py.  

**```HTRSET```** sets the parameters for output 1 and 2 (heaters)  
*Example Syntax* 
```bash
HTRSET <output>, <resistance>, <max current>, <max user current>, <current/power>
```  
  *output* specifies output 1 or 2  
  *htr resistance* 1 = 25 Ohms, 2 = 50 Ohms  
  *max current* shows max current (relevant for closed loop/PID)
  0 = User Specified, 1 = 0.707 A, 2 = 1 A, 3 = 1.141 A, 4 = 2 A   
  *max user current* if max current = 0, this is the current the user has set as the max  
  *current/power* specifies what format the output is display in, and what the ```MOUT``` percentage determines  

Recommended Arguments:   
  HTRSET 1,2,0,0.1,1    
  HTRSET 2, 1,0,+1.732,1     

*Note Output 1 parameters can vary (variable resistance, variable max current, max power 75W) but Output 2 is fixed and low power (max current 0.1 A, max power 1W). It may not be possible to use HTRSET to change the settings on output 2.   



**```ANALOG```** sets the parameters for output 3 and 4 (switches)  
*Example Syntax* 
```bash
ANALOG <output>, <input>,<units>,<high value>, <low value>, <polarity>
```  
  *output* specifies output 3 or 5   
  *input* For closed loop/PID specifies which input to monitor 0 = none, 1 = Input A, 2 =Input B, 3 = Input C, 4 = Input D (5 = Input D2, 6 = Input D3, 7 = Input D4, 8 = Input D5 for 3062 option)  
  *units* specifies what units to base output voltage on (also for closed loop/PID)  
  *high value* when in Monitor Out Mode, specifies data where we reach 100% output. Units are same as those specified in <units>  
  *low value* when in Monitor Out Mode, this parameter represents the data where we reach -100% output if in the bipolar, or 0% output
  if positive only. Units are same as those specified in <units>  
  *polarity* Specifies output voltage is 0 = unipolar (positive output only) or 1 = bipolar (positive or negative output)  

Reccomended Arguments:   
  3, 0,1,+5.00000,+0.00000,0    
  4, 0,1,+5.00000,+0.00000,0   

#### Command Line Usage Examples
**1)** Let's say I want to set my output 1 to a resistance of 50ohms, user specified 0.1A max current, measured in current units. I execute:   
```bash
lakeshore350 -outputs-set-params
```
This returns a prompt: ```Enter output number (1, 2, 3, or 4): ```   

I enter 1, and then I am prompted for HTRSET args (minus the first arg, for output number).  

I enter ```2, 0, 0.1, 1```.

Now my output 1 parameters are set and I can double check with ```lakeshore350 --outputs-query 1```

**2)** Let's say I want to set my output 3 to no control input, kelvin units, 5 V max, no min, 0 polarity. I execute:  

```bash
lakeshore350 -outputs-set-params
```
This returns a prompt: ```Enter output number (1, 2, 3, or 4): ```   

I enter 3, and then I am prompted for ANALOG args (minus the first arg, for output number).  

I enter ``` 0,1,+5.00000,+0.00000,0```.

Now my output 3 parameters are set and I can double check with ```lakeshore350 --outputs-query 3```

### Using outputs-set
```--outputs-set <output> <percent value>``` is the primary method of turning on the heaters (outputs 1 and 2) and switches (outputs 3 and 4).  

#### Serial Syntax 
**```MOUT```** sets the percent output for each output. For the heaters output 1 and 2 this is the percentage of max current (in the current setting) and for the switches output 3 and 4 this the percentage of max voltage (5V). Note that the max current is different for output 1 and 2.   

*Example Syntax*
```bash
MOUT <output> <value> 
```  
  <output> specifies which output 1, 2, 3, 4  
  <value> percentage  

#### Command Line Usage Examples 
**1)** Let's say I want to turn on the 3-switch. First I always ```outputs-query 4``` to make sure my max voltage is 5V.   

Then I execute:  
```bash
lakeshore350 --outputs-set 4 100
```

Now there are 5V going through the 3-switch. 

**2)** Let's say I want to turn on the 4-pump heater. *Do not just turn it on to 100%, power up slowly*  

```bash
lakeshore350 --outputs-set 1 10%
```
This sets output 1 to 10%. Output 1 max current is 0.1A so 10% sends in 10mA, or a voltage of 3V for the 300Ohm resistance heater. 


## Requirements

- Python 3.7+
- pyserial
- Lake Shore 350 connected via USB serial




