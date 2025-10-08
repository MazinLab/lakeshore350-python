#!/usr/bin/env python3
"""
TEMPERATURE DATA PLOTTING TOOL
==============================

OVERVIEW:
---------
This tool allows you to plot temperature data from CSV files in the temps/ directory.
You can select specific columns by name and plot temperature vs time in minutes.

FEATURES:
---------
- Plot any temperature column from CSV files
- Time axis in minutes since start of run
- Automatic PNG export to plots/ folder
- Handle non-numeric data (T_OVER, NO_RESPONSE)
- Interactive column selection
- Multiple file support

USAGE:
------
python plot_temperature.py [csv_file] [column1] [column2] [column3] ...

Examples:
    python plot_temperature.py                                    # Interactive mode
    python plot_temperature.py temps/2025-10-08_temperature_log_1.csv 4K_Stage_Temp_K
    python plot_temperature.py temps/2025-10-08_temperature_log_1.csv 4K_Stage_Temp_K 3_Head_Temp_K
    python plot_temperature.py temps/latest.csv 3_Head_Temp_K 4_Head_Temp_K 3_Pump_Temp_K

Available Columns:
    - 4K_Stage_Temp_K
    - 50K_Stage_Temp_K  
    - Device_Stage_Temp_K
    - 3_Head_Temp_K
    - 4_Head_Temp_K
    - 3_Pump_Temp_K
    - 4_Pump_Temp_K
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import argparse
import os
import sys
import glob
import numpy as np

class TemperaturePlotter:
    """
    TEMPERATURE DATA PLOTTING CLASS
    ===============================
    
    Handles CSV data loading, processing, and plotting of temperature data.
    """
    
    def __init__(self):
        """Initialize the temperature plotter"""
        # Create plots directory if it doesn't exist
        self.plots_dir = "plots"
        os.makedirs(self.plots_dir, exist_ok=True)
        print(f"Plots will be saved to: {self.plots_dir}/")
    
    def load_csv_data(self, csv_file):
        """
        LOAD AND PROCESS CSV DATA
        =========================
        
        Args:
            csv_file (str): Path to CSV file
            
        Returns:
            pandas.DataFrame: Processed temperature data
        """
        try:
            print(f"Loading data from: {csv_file}")
            
            # Read CSV with whitespace-separated values
            df = pd.read_csv(csv_file, sep=r'\s+', engine='python')
            
            print(f"Loaded {len(df)} data points")
            print(f"Available columns: {list(df.columns)}")
            
            # Convert timestamp to datetime
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            # Calculate minutes since start
            start_time = df['Timestamp'].iloc[0]
            df['Minutes_Since_Start'] = (df['Timestamp'] - start_time).dt.total_seconds() / 60
            
            return df
            
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None
    
    def get_available_columns(self, df):
        """
        GET TEMPERATURE COLUMNS
        =======================
        
        Args:
            df (pandas.DataFrame): Data frame
            
        Returns:
            list: List of temperature column names
        """
        # Filter for temperature columns (ending with _K or containing Temp)
        temp_columns = [col for col in df.columns 
                       if col.endswith('_K') or 'Temp' in col]
        temp_columns = [col for col in temp_columns 
                       if col not in ['Timestamp', 'Date', 'Time']]
        return temp_columns
    
    def clean_temperature_data(self, df, column):
        """
        CLEAN TEMPERATURE DATA
        ======================
        
        Removes non-numeric values like 'T_OVER', 'NO_RESPONSE', etc.
        
        Args:
            df (pandas.DataFrame): Data frame
            column (str): Column name to clean
            
        Returns:
            pandas.DataFrame: Cleaned data frame
        """
        print(f"Cleaning data for column: {column}")
        
        # Create a copy to avoid modifying original
        clean_df = df.copy()
        
        # Count original NaN values
        original_nan_count = clean_df[column].isna().sum()
        
        # Convert column to numeric, setting errors='coerce' to replace non-numeric with NaN
        clean_df[column] = pd.to_numeric(clean_df[column], errors='coerce')
        
        # Count non-numeric values that were converted to NaN
        total_nan_count = clean_df[column].isna().sum()
        non_numeric_count = total_nan_count - original_nan_count
        
        if non_numeric_count > 0:
            print(f"  Found {non_numeric_count} non-numeric values (T_OVER, NO_RESPONSE, etc.) - skipping these data points")
        
        # Remove rows with NaN in the temperature column
        clean_df = clean_df.dropna(subset=[column])
        
        print(f"  {len(clean_df)} valid numeric data points remaining")
        return clean_df
    
    def plot_temperature(self, df, columns, csv_file):
        """
        PLOT TEMPERATURE DATA (SINGLE OR MULTIPLE COLUMNS)
        ==================================================
        
        Args:
            df (pandas.DataFrame): Clean data frame
            columns (list): List of temperature columns to plot
            csv_file (str): Original CSV file name for title
        """
        if isinstance(columns, str):
            columns = [columns]
        
        print(f"Plotting {', '.join(columns)} vs time...")
        
        # Create figure and axis
        plt.figure(figsize=(12, 8))
        
        # Define colors for multiple lines
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        # Plot each column
        for i, column in enumerate(columns):
            color = colors[i % len(colors)]
            
            # Get clean data for this column
            clean_col_df = self.clean_temperature_data(df, column)
            if len(clean_col_df) == 0:
                print(f"  Warning: No valid data for {column}, skipping...")
                continue
            
            # Plot line
            plt.plot(clean_col_df['Minutes_Since_Start'], clean_col_df[column], 
                    color=color, linewidth=1.5, marker='o', markersize=3, alpha=0.7,
                    label=column.replace("_", " "))
        
        # Customize plot
        plt.xlabel('Time (minutes since start)', fontsize=12)
        plt.ylabel('Temperature (K)', fontsize=12)
        
        if len(columns) == 1:
            plt.title(f'Temperature vs Time: {columns[0].replace("_", " ")}\nData from: {os.path.basename(csv_file)}', 
                     fontsize=14, pad=20)
        else:
            plt.title(f'Temperature vs Time: Multiple Sensors\nData from: {os.path.basename(csv_file)}', 
                     fontsize=14, pad=20)
        
        # Add legend for multiple columns
        if len(columns) > 1:
            plt.legend(loc='best', fontsize=10)
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Format axes
        plt.ticklabel_format(style='plain', axis='y')
        
        # Add statistics text box for multiple columns
        if len(columns) > 1:
            stats_text = self.get_multi_column_statistics_text(df, columns)
        else:
            clean_df = self.clean_temperature_data(df, columns[0])
            stats_text = self.get_statistics_text(clean_df, columns[0])
        
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Tight layout
        plt.tight_layout()
        
        # Save plot
        if len(columns) == 1:
            plot_filename = f"{columns[0]}_{os.path.splitext(os.path.basename(csv_file))[0]}.png"
        else:
            plot_filename = f"multi_temp_{os.path.splitext(os.path.basename(csv_file))[0]}.png"
        
        plot_path = os.path.join(self.plots_dir, plot_filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        
        print(f"Plot saved to: {plot_path}")
        
        # Show plot
        plt.show()
    
    def get_statistics_text(self, df, column):
        """
        GENERATE STATISTICS TEXT
        ========================
        
        Args:
            df (pandas.DataFrame): Data frame
            column (str): Temperature column
            
        Returns:
            str: Statistics text for plot
        """
        temps = df[column]
        duration_minutes = df['Minutes_Since_Start'].iloc[-1] - df['Minutes_Since_Start'].iloc[0]
        
        stats = f"Statistics:\n"
        stats += f"Duration: {duration_minutes:.1f} min\n"
        stats += f"Points: {len(temps)}\n"
        stats += f"Min: {temps.min():.2f} K\n"
        stats += f"Max: {temps.max():.2f} K\n"
        stats += f"Mean: {temps.mean():.2f} K\n"
        stats += f"Std: {temps.std():.2f} K"
        
        return stats
    
    def get_multi_column_statistics_text(self, df, columns):
        """
        GENERATE MULTI-COLUMN STATISTICS TEXT
        ====================================
        
        Args:
            df (pandas.DataFrame): Data frame
            columns (list): List of temperature columns
            
        Returns:
            str: Statistics text for multi-column plot
        """
        duration_minutes = df['Minutes_Since_Start'].iloc[-1] - df['Minutes_Since_Start'].iloc[0]
        
        stats = f"Statistics:\n"
        stats += f"Duration: {duration_minutes:.1f} min\n"
        stats += f"Columns: {len(columns)}\n\n"
        
        for column in columns:
            clean_col_df = self.clean_temperature_data(df, column)
            if len(clean_col_df) > 0:
                temps = clean_col_df[column]
                short_name = column.replace("_Temp_K", "").replace("_Stage", "").replace("_", " ")
                stats += f"{short_name}:\n"
                stats += f"  Min: {temps.min():.1f} K\n"
                stats += f"  Max: {temps.max():.1f} K\n"
                stats += f"  Mean: {temps.mean():.1f} K\n\n"
        
        return stats.rstrip('\n')
    
    def list_csv_files(self):
        """
        LIST AVAILABLE CSV FILES
        ========================
        
        Returns:
            list: List of CSV files in temps/ directory
        """
        csv_files = glob.glob("temps/*.csv")
        csv_files.sort()
        return csv_files
    
    def interactive_mode(self):
        """
        INTERACTIVE MODE
        ================
        
        Allows user to select CSV file and column interactively
        """
        print("\n" + "="*60)
        print("INTERACTIVE TEMPERATURE PLOTTING")
        print("="*60)
        
        # List available CSV files
        csv_files = self.list_csv_files()
        if not csv_files:
            print("No CSV files found in temps/ directory!")
            return
        
        print(f"\nAvailable CSV files:")
        for i, file in enumerate(csv_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        # Select CSV file
        try:
            choice = int(input(f"\nSelect CSV file (1-{len(csv_files)}): ")) - 1
            if choice < 0 or choice >= len(csv_files):
                print("Invalid choice!")
                return
            csv_file = csv_files[choice]
        except ValueError:
            print("Invalid input!")
            return
        
        # Load data
        df = self.load_csv_data(csv_file)
        if df is None:
            return
        
        # Get available columns
        temp_columns = self.get_available_columns(df)
        if not temp_columns:
            print("No temperature columns found!")
            return
        
        print(f"\nAvailable temperature columns:")
        for i, col in enumerate(temp_columns):
            print(f"  {i+1}. {col}")
        
        # Select columns (single or multiple)
        print(f"\nSelect columns to plot:")
        print(f"  - Single column: Enter one number (e.g., 1)")
        print(f"  - Multiple columns: Enter numbers separated by commas (e.g., 1,3,5)")
        
        try:
            choice_input = input(f"Selection: ").strip()
            
            if ',' in choice_input:
                # Multiple columns
                choices = [int(x.strip()) - 1 for x in choice_input.split(',')]
                columns = []
                for choice in choices:
                    if 0 <= choice < len(temp_columns):
                        columns.append(temp_columns[choice])
                    else:
                        print(f"Invalid choice: {choice + 1}")
                        return
            else:
                # Single column
                choice = int(choice_input) - 1
                if choice < 0 or choice >= len(temp_columns):
                    print("Invalid choice!")
                    return
                columns = [temp_columns[choice]]
                
        except ValueError:
            print("Invalid input!")
            return
        
        if not columns:
            print("No valid columns selected!")
            return
        
        print(f"Selected columns: {', '.join(columns)}")
        
        # Process and plot
        self.process_and_plot(df, columns, csv_file)
    
    def process_and_plot(self, df, columns, csv_file):
        """
        PROCESS AND PLOT DATA (SINGLE OR MULTIPLE COLUMNS)
        ==================================================
        
        Args:
            df (pandas.DataFrame): Raw data frame
            columns (list or str): Column(s) to plot
            csv_file (str): CSV file path
        """
        # Ensure columns is a list
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Column(s) {missing_columns} not found in data!")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Check if any columns have valid data
        valid_columns = []
        for column in columns:
            clean_df = self.clean_temperature_data(df, column)
            if len(clean_df) > 0:
                valid_columns.append(column)
            else:
                print(f"Warning: No valid data points found for column '{column}', excluding from plot")
        
        if not valid_columns:
            print(f"Error: No valid data points found for any selected columns")
            return
        
        # Plot data
        self.plot_temperature(df, valid_columns, csv_file)


def main():
    """
    MAIN FUNCTION
    =============
    
    Handles command line arguments and runs the plotter
    """
    parser = argparse.ArgumentParser(
        description='Plot temperature data from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python plot_temperature.py                                    # Interactive mode
    python plot_temperature.py temps/2025-10-08_temperature_log_1.csv 4K_Stage_Temp_K
    python plot_temperature.py temps/2025-10-08_temperature_log_1.csv 4K_Stage_Temp_K 3_Head_Temp_K
    python plot_temperature.py temps/latest.csv 3_Head_Temp_K 4_Head_Temp_K 3_Pump_Temp_K

Available columns: 4K_Stage_Temp_K, 50K_Stage_Temp_K, Device_Stage_Temp_K,
                   3_Head_Temp_K, 4_Head_Temp_K, 3_Pump_Temp_K, 4_Pump_Temp_K
        """)
    
    parser.add_argument('csv_file', nargs='?', 
                       help='Path to CSV file (e.g., temps/2025-10-08_temperature_log_1.csv)')
    parser.add_argument('columns', nargs='*',
                       help='Temperature column name(s) (e.g., 4K_Stage_Temp_K 3_Head_Temp_K)')
    
    args = parser.parse_args()
    
    # Create plotter
    plotter = TemperaturePlotter()
    
    if args.csv_file and args.columns:
        # COMMAND LINE MODE
        if not os.path.exists(args.csv_file):
            print(f"Error: CSV file '{args.csv_file}' not found!")
            sys.exit(1)
        
        # Load data
        df = plotter.load_csv_data(args.csv_file)
        if df is None:
            sys.exit(1)
        
        # Process and plot
        plotter.process_and_plot(df, args.columns, args.csv_file)
        
    else:
        # INTERACTIVE MODE
        plotter.interactive_mode()


if __name__ == "__main__":
    main()
