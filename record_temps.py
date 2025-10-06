#!/usr/bin/env python3
"""
Temperature        self.csv_headers = [
            "Timestamp",
            "Date", 
            "Time",
            "4K_Stage_Temp_K",
            "50K_Stage_Temp_K", 
            "Device_Stage_Temp_K",
            "3_Head_Res_Ohm",
            "3_Head_Temp_K",
            "4_Head_Res_Ohm",
            "4_Head_Temp_K",
            "3_Pump_Volt_V",
            "3_Pump_Temp_K",
            "4_Pump_Volt_V",
            "4_Pump_Temp_K"
        ]
        
        # Define column widths for nice formatting (adjusted for proper alignment)
        # Timestamp, Date, Time, 4K_Stage, 50K_Stage, Device_Stage, 3_Head_Res, 3_Head_Temp, 4_Head_Res, 4_Head_Temp, 3_Pump_Volt, 3_Pump_Temp, 4_Pump_Volt, 4_Pump_Temp
        self.column_widths = [28, 12, 12, 17, 17, 20, 18, 16, 18, 16, 17, 16, 17, 16]
Continuously records temperatures every 30 seconds and saves to CSV
"""

import time
import csv
import os
from datetime import datetime
import sys

# Add the lakeshore350 module to the path
sys.path.append('/home/kids/lakeshore350-python')

from lakeshore350.temperature import TemperatureReader
from lakeshore350.head3_calibration import convert_3head_resistance_to_temperature
from lakeshore350.head4_calibration import convert_4head_resistance_to_temperature
from lakeshore350.pump_calibration import convert_pump_voltage_to_temperature

class TemperatureRecorder:
    def __init__(self):
        # Initialize temperature reader
        self.temp_reader = TemperatureReader()
        
        # Data storage
        self.temperature_data = []
        
        # CSV file setup with automatic numbering
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create temps directory if it doesn't exist
        os.makedirs("temps", exist_ok=True)
        
        # Find next available filename
        self.csv_filename = self._get_next_csv_filename()
        
        # CSV headers
        self.headers = [
            "Timestamp",
            "Date", 
            "Time",
            "4K_Stage_Temp_K",
            "50K_Stage_Temp_K", 
            "Device_Stage_Temp_K",
            "3_Head_Res_Ohm",
            "3_Head_Temp_K",
            "4_Head_Res_Ohm",
            "4_Head_Temp_K",
            "3_Pump_Temp_K",
            "4_Pump_Temp_K"
        ]
        
        # Define column widths for nice formatting (adjusted for proper alignment)
        # Timestamp, Date, Time, 4K_Stage, 50K_Stage, Device_Stage, 3_Head_Res, 3_Head_Temp, 4_Head_Res, 4_Head_Temp, 3_Pump_Volt, 3_Pump_Temp, 4_Pump_Volt, 4_Pump_Temp
        self.column_widths = [28, 12, 12, 17, 17, 20, 18, 16, 18, 16, 17, 16, 17, 16]
        
        # Don't print header yet - will be done in run() method
        
    def _get_next_csv_filename(self):
        """Find the next available CSV filename with automatic numbering"""
        base_filename = f"temps/{self.start_date}_temperature_log.csv"
        
        # If the base filename doesn't exist, use it
        if not os.path.exists(base_filename):
            return base_filename
        
        # Otherwise, find the next numbered version
        counter = 1
        while True:
            numbered_filename = f"temps/{self.start_date}_temperature_log_{counter}.csv"
            if not os.path.exists(numbered_filename):
                return numbered_filename
            counter += 1
        
    def print_formatted_header(self):
        """Print nicely formatted header to terminal"""
        # Print header row
        header_line = ""
        for i, header in enumerate(self.headers):
            header_line += f"{header:<{self.column_widths[i]}}"
        print(header_line)
        
        # Print separator line
        separator_line = ""
        for width in self.column_widths:
            separator_line += "-" * width
        print(separator_line)
    
    def print_formatted_row(self, data_row):
        """Print nicely formatted data row to terminal"""
        formatted_line = ""
        for i, value in enumerate(data_row):
            # Special formatting for different columns
            if i == 6 and isinstance(value, float):
                # 3-head resistance (4 decimal places)
                formatted_value = f"{value:.4f}"
            elif i == 7 and isinstance(value, float):
                # 3-head temperature (3 decimal places)
                formatted_value = f"{value:.3f}"
            elif i == 8 and isinstance(value, float):
                # 4-head resistance (4 decimal places)
                formatted_value = f"{value:.4f}"
            elif i == 9 and isinstance(value, float):
                # 4-head temperature (3 decimal places)
                formatted_value = f"{value:.3f}"
            elif isinstance(value, float):
                # Other numbers (2 decimal places)
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            formatted_line += f"{formatted_value:<{self.column_widths[i]}}"
        print(formatted_line)
        
    def get_temperatures(self):
        """Get all required temperatures and heater status"""
        current_time = datetime.now()
        timestamp = current_time.isoformat()
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")
        
        try:
            # Read temperatures
            # 4K Stage (Channel 2)
            temp_4k = self.temp_reader.send_command("KRDG? 2")
            try:
                temp_4k_val = float(temp_4k) if temp_4k and temp_4k != "T_OVER" and temp_4k != "NO_RESPONSE" else temp_4k
            except ValueError:
                temp_4k_val = temp_4k
            
            # 50K Stage (Channel 3)  
            temp_50k = self.temp_reader.send_command("KRDG? 3")
            try:
                temp_50k_val = float(temp_50k) if temp_50k and temp_50k != "T_OVER" and temp_50k != "NO_RESPONSE" else temp_50k
            except ValueError:
                temp_50k_val = temp_50k
            
            # Device Stage (Input B)
            temp_device = self.temp_reader.read_temperature('B')
            
            # 3-head resistance (Input A) and calibrated temperature
            resistance_3_head = self.temp_reader.read_temperature('A')
            
            # Convert 3-head resistance to temperature using calibration
            if isinstance(resistance_3_head, float) and resistance_3_head > 0:
                temp_3_head = convert_3head_resistance_to_temperature(resistance_3_head)
            else:
                temp_3_head = None
            
            # 4-head resistance (Input C) and calibrated temperature
            resistance_4_head = self.temp_reader.read_temperature('C')
            
            # Convert 4-head resistance to temperature using calibration
            if isinstance(resistance_4_head, float) and resistance_4_head > 0:
                temp_4_head = convert_4head_resistance_to_temperature(resistance_4_head)
            else:
                temp_4_head = None
            
            # 3-pump voltage (Input D) and calibrated temperature
            voltage_3_pump = self.temp_reader.read_voltage('D')
            
            # Convert 3-pump voltage to temperature using calibration
            if isinstance(voltage_3_pump, float) and voltage_3_pump > 0:
                temp_3_pump = convert_pump_voltage_to_temperature(voltage_3_pump)
            else:
                temp_3_pump = None
            
            # 4-pump voltage (Channel 5) and calibrated temperature
            voltage_4_pump_response = self.temp_reader.send_command("VRDG? 5")
            try:
                if voltage_4_pump_response and voltage_4_pump_response != "V_OVER" and voltage_4_pump_response != "NO_RESPONSE":
                    voltage_4_pump = float(voltage_4_pump_response)
                    temp_4_pump = convert_pump_voltage_to_temperature(voltage_4_pump)
                else:
                    voltage_4_pump = None
                    temp_4_pump = None
            except ValueError:
                voltage_4_pump = None
                temp_4_pump = None
            
            return {
                "timestamp": timestamp,
                "date": date_str,
                "time": time_str,
                "temp_4k": temp_4k_val,
                "temp_50k": temp_50k_val,
                "temp_device": temp_device,
                "resistance_3_head": resistance_3_head,
                "temp_3_head": temp_3_head,
                "resistance_4_head": resistance_4_head,
                "temp_4_head": temp_4_head,
                "voltage_3_pump": voltage_3_pump,
                "temp_3_pump": temp_3_pump,
                "voltage_4_pump": voltage_4_pump,
                "temp_4_pump": temp_4_pump
            }
            
        except Exception as e:
            print(f"Error reading temperatures: {e}")
            return None
    
    def format_csv_row(self, data):
        """Format data dictionary as CSV row"""
        try:
            row = [
                data["timestamp"],
                data["date"],
                data["time"],
                data["temp_4k"],
                data["temp_50k"],
                data["temp_device"],
                data["resistance_3_head"],
                data["temp_3_head"],
                data["resistance_4_head"],
                data["temp_4_head"],
                data["voltage_3_pump"],
                data["temp_3_pump"],
                data["voltage_4_pump"],
                data["temp_4_pump"]
            ]
            return row
        except Exception as e:
            print(f"Error formatting CSV row: {e}")
            return None
    
    def save_to_csv(self):
        """Save all recorded data to CSV file"""
        try:
            with open(self.csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)
                writer.writerows(self.temperature_data)
        except Exception as e:
            print(f"Error saving CSV file: {e}")
    
    def create_formatted_csv(self):
        """Create CSV file with nicely formatted columns"""
        try:
            with open(self.csv_filename, 'w', newline='') as csvfile:
                # Write formatted header
                header_line = ""
                for i, header in enumerate(self.headers):
                    if i == len(self.headers) - 1:  # Last column
                        header_line += header
                    else:
                        header_line += f"{header:<{self.column_widths[i]}}"
                csvfile.write(header_line + "\n")
        except Exception as e:
            print(f"Error creating CSV file: {e}")
    
    def append_to_formatted_csv(self, data_row):
        """Append a formatted row to the CSV file"""
        try:
            with open(self.csv_filename, 'a', newline='') as csvfile:
                # Write formatted data row
                formatted_line = ""
                for i, value in enumerate(data_row):
                    # Special formatting for different columns
                    if i == 6 and isinstance(value, float):
                        # 3-head resistance (4 decimal places)
                        formatted_value = f"{value:.4f}"
                    elif i == 7 and isinstance(value, float):
                        # 3-head temperature (3 decimal places)
                        formatted_value = f"{value:.3f}"
                    elif i == 8 and isinstance(value, float):
                        # 4-head resistance (4 decimal places)
                        formatted_value = f"{value:.4f}"
                    elif i == 9 and isinstance(value, float):
                        # 4-head temperature (3 decimal places)
                        formatted_value = f"{value:.3f}"
                    elif isinstance(value, float):
                        # Other numbers (2 decimal places)
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    
                    if i == len(data_row) - 1:  # Last column
                        formatted_line += formatted_value
                    else:
                        formatted_line += f"{formatted_value:<{self.column_widths[i]}}"
                csvfile.write(formatted_line + "\n")
        except Exception as e:
            print(f"Error appending to CSV file: {e}")
    
    def run(self):
        """Main recording loop"""
        # Print startup information first
        print(f"Starting temperature recording...")
        print(f"Recording interval: 30 seconds")
        print(f"CSV file will be saved as: {self.csv_filename}")
        print(f"Press Ctrl+C to stop recording and save data")
        print("-" * 80)
        print()  # Empty line
        
        # Now print the formatted header
        self.print_formatted_header()
        
        # Create the CSV file immediately with formatted header
        self.create_formatted_csv()
        
        try:
            while True:
                # Get current readings
                data = self.get_temperatures()
                
                if data:
                    # Format as CSV row
                    csv_row = self.format_csv_row(data)
                    
                    if csv_row:
                        # Store data
                        self.temperature_data.append(csv_row)
                        
                        # Print to terminal with nice formatting
                        self.print_formatted_row(csv_row)
                        
                        # Append to CSV file immediately
                        self.append_to_formatted_csv(csv_row)
                
                # Wait 30 seconds
                time.sleep(30)
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print(f"\n\nStopping recording.")
            print(f"Temperature log saved successfully!")
            print(f"Total readings recorded: {len(self.temperature_data)}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            # Still save using the formatted method as backup
            self.save_to_csv()

def main():
    """Main function"""
    recorder = TemperatureRecorder()
    recorder.run()

if __name__ == "__main__":
    main()
