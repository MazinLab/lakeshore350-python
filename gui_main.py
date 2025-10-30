
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel, QTabWidget,
    QHBoxLayout, QLineEdit, QFrame, QGroupBox
)

# Import your output querying logic
try:
    from lakeshore350.outputs import OutputController
except ImportError:
    OutputController = None  # Fallback for initial scaffold

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lakeshore 350 Controller")
        self.setGeometry(100, 100, 500, 400)

        # Create tab widget
        tabs = QTabWidget()

        # Home tab
        home_tab = QWidget()
        home_layout = QVBoxLayout()
        home_tab.setLayout(home_layout)
        tabs.addTab(home_tab, "Home")

        # Outputs tab
        outputs_tab = QWidget()
        outputs_layout = QVBoxLayout()
        outputs_tab.setLayout(outputs_layout)

        self.info_label = QLabel("Lakeshore 350 Outputs")
        outputs_layout.addWidget(self.info_label)

        self.query_button = QPushButton("Query Outputs")
        self.query_button.clicked.connect(self.query_all_outputs)
        outputs_layout.addWidget(self.query_button)

        # Output Percentage Section
        percent_group = QGroupBox("Set Output Percentage")
        percent_group_layout = QVBoxLayout()
        percent_layout = QHBoxLayout()
        self.percent_output_num = QLineEdit()
        self.percent_output_num.setPlaceholderText("Output # (1-4)")
        self.percent_value = QLineEdit()
        self.percent_value.setPlaceholderText("Percent (0-100)")
        self.set_percent_button = QPushButton("Set %")
        self.set_percent_button.clicked.connect(self.set_output_percent)
        percent_layout.addWidget(self.percent_output_num)
        percent_layout.addWidget(self.percent_value)
        percent_layout.addWidget(self.set_percent_button)
        percent_group_layout.addLayout(percent_layout)
        percent_group.setLayout(percent_group_layout)
        outputs_layout.addWidget(percent_group)

        # Divider
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        outputs_layout.addWidget(line1)

        # Output Range Section
        range_group = QGroupBox("Set Output Range")
        range_group_layout = QVBoxLayout()
        range_layout = QHBoxLayout()
        self.range_output_num = QLineEdit()
        self.range_output_num.setPlaceholderText("Output # (1-4)")
        self.range_value = QLineEdit()
        self.range_value.setPlaceholderText("Range Value")
        self.set_range_button = QPushButton("Set Range")
        self.set_range_button.clicked.connect(self.set_output_range)
        range_layout.addWidget(self.range_output_num)
        range_layout.addWidget(self.range_value)
        range_layout.addWidget(self.set_range_button)
        range_group_layout.addLayout(range_layout)
        range_group.setLayout(range_group_layout)
        outputs_layout.addWidget(range_group)

        # Divider
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        outputs_layout.addWidget(line2)

        # Output Params Section
        params_group = QGroupBox("Set Output Params")
        params_group_layout = QVBoxLayout()
        params_layout = QHBoxLayout()
        self.params_output_num = QLineEdit()
        self.params_output_num.setPlaceholderText("Output # (1-4)")
        self.params_values = QLineEdit()
        self.params_values.setPlaceholderText("Params (comma separated)")
        self.set_params_button = QPushButton("Set Params")
        self.set_params_button.clicked.connect(self.set_output_params)
        params_layout.addWidget(self.params_output_num)
        params_layout.addWidget(self.params_values)
        params_layout.addWidget(self.set_params_button)
        params_group_layout.addLayout(params_layout)
        params_group.setLayout(params_group_layout)
        outputs_layout.addWidget(params_group)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        outputs_layout.addWidget(self.output_text)

        tabs.addTab(outputs_tab, "Outputs")

        # Temperatures tab
        temps_tab = QWidget()
        temps_layout = QVBoxLayout()
        temps_tab.setLayout(temps_layout)

        self.temps_label = QLabel("Lakeshore 350 Temperatures")
        temps_layout.addWidget(self.temps_label)

        self.query_temps_button = QPushButton("Query Temperatures")
        self.query_temps_button.clicked.connect(self.query_temperatures)
        temps_layout.addWidget(self.query_temps_button)

        self.temps_text = QTextEdit()
        self.temps_text.setReadOnly(True)
        temps_layout.addWidget(self.temps_text)

        tabs.addTab(temps_tab, "Temperatures")

        # Set Home tab as default
        tabs.setCurrentIndex(0)

        # Set central widget
        self.setCentralWidget(tabs)

    def set_output_percent(self):
        if OutputController:
            try:
                output_num = int(self.percent_output_num.text())
                percent = float(self.percent_value.text())
                controller = OutputController()
                controller.set_outputs(output_num, percent)
                self.output_text.append(f"Set Output {output_num} to {percent}%")
            except Exception as e:
                self.output_text.append(f"Error: {e}")
        else:
            self.output_text.append("OutputController not found.")

    def set_output_range(self):
        if OutputController:
            try:
                output_num = int(self.range_output_num.text())
                range_val = int(self.range_value.text())
                controller = OutputController()
                controller.set_heater_range(output_num, range_val)
                self.output_text.append(f"Set Output {output_num} range to {range_val}")
            except Exception as e:
                self.output_text.append(f"Error: {e}")
        else:
            self.output_text.append("OutputController not found.")

    def set_output_params(self):
        if OutputController:
            try:
                output_num = int(self.params_output_num.text())
                params = [p.strip() for p in self.params_values.text().split(",")]
                controller = OutputController()
                controller.set_output_params(output_num, params)
                self.output_text.append(f"Set Output {output_num} params to {params}")
            except Exception as e:
                self.output_text.append(f"Error: {e}")
        else:
            self.output_text.append("OutputController not found.")
    def query_temperatures(self):
        # Query all temperatures (A, B, C, D1, D2, D3, D4, D5) and display in GUI
        try:
            from lakeshore350.temperature import TemperatureReader
            from lakeshore350.head3_calibration import convert_3head_resistance_to_temperature
            from lakeshore350.head4_calibration import convert_4head_resistance_to_temperature
            from lakeshore350.pumps_calibration import voltage_to_temperature
            from lakeshore350.panel_display import get_display_name
        except ImportError:
            self.temps_text.setText("Temperature modules not found. Please check your installation.")
            return

        port = "/dev/ttyUSB2"
        temp_reader = TemperatureReader(port=port)
        output_lines = []

        # Inputs A, B, C
        temp_a = temp_reader.read_temperature('A')
        temp_b = temp_reader.read_temperature('B')
        temp_c = temp_reader.read_temperature('C')

        a_display = get_display_name(port=port, input_name='A') or '3-head'
        b_display = get_display_name(port=port, input_name='B') or 'Empty'
        c_display = get_display_name(port=port, input_name='C') or '4-head'
        a_label = f"Input A ({a_display})"
        b_label = f"Input B ({b_display})"
        c_label = f"Input C ({c_display})"

        if isinstance(temp_a, float):
            temp_a_cal = convert_3head_resistance_to_temperature(temp_a)
            if temp_a_cal is not None:
                output_lines.append(f"  {a_label}: {temp_a:.4f} Ω → {temp_a_cal:.3f} K")
            else:
                output_lines.append(f"  {a_label}: {temp_a:.4f} Ω → None")
        else:
            output_lines.append(f"  {a_label}: {temp_a}")

        if isinstance(temp_b, float):
            output_lines.append(f"  {b_label}: {temp_b:.3f} K")
        else:
            output_lines.append(f"  {b_label}: {temp_b}")

        if isinstance(temp_c, float):
            temp_c_calibrated = temp_c + 34.56
            temp_c_temp = convert_4head_resistance_to_temperature(temp_c_calibrated)
            line = f"  {c_label}: {temp_c:.4f} Ω (raw), {temp_c_calibrated:.4f} Ω (calibrated) → "
            if temp_c_temp is not None:
                line += f"{temp_c_temp:.3f} K"
            else:
                line += "None"
            output_lines.append(line)
        else:
            output_lines.append(f"  {c_label}: {temp_c}")

        # Special Inputs
        output_lines.append("\nSpecial Inputs:")
        d1_voltage = temp_reader.read_sensor('D1')
        d2_temp = temp_reader.read_temperature('D2')
        d3_temp = temp_reader.read_temperature('D3')
        d4_voltage = temp_reader.read_sensor('D4')
        d5_voltage = temp_reader.read_sensor('D5')

        d1_display = get_display_name(port=port, input_name='D1') or 'Empty'
        d2_display = get_display_name(port=port, input_name='D2') or '50K'
        d3_display = get_display_name(port=port, input_name='D3') or '4K'
        d4_display = get_display_name(port=port, input_name='D4') or '3-pump'
        d5_display = get_display_name(port=port, input_name='D5') or '4-pump'
        d1_name = f"Input D1 ({d1_display})"
        d2_name = f"Input D2 ({d2_display})" if 'stage' in d2_display.lower() or d2_display.lower().endswith('k') else f"Input D2 ({d2_display} Stage)"
        d3_name = f"Input D3 ({d3_display})"
        d4_name = f"Input D4 ({d4_display})"
        d5_name = f"Input D5 ({d5_display})"

        # D1
        if isinstance(d1_voltage, float):
            d1_temp = voltage_to_temperature(d1_voltage)
            if d1_temp is not None:
                output_lines.append(f"  {d1_name}: {d1_voltage:.4f} V → {d1_temp:.3f} K")
            else:
                output_lines.append(f"  {d1_name}: {d1_voltage:.4f} V → None")
        else:
            output_lines.append(f"  {d1_name}: {d1_voltage}")
        # D2
        if isinstance(d2_temp, float):
            output_lines.append(f"  {d2_name}: {d2_temp:.3f} K")
        else:
            output_lines.append(f"  {d2_name}: {d2_temp}")
        # D3
        if isinstance(d3_temp, float):
            output_lines.append(f"  {d3_name}: {d3_temp:.3f} K")
        else:
            output_lines.append(f"  {d3_name}: {d3_temp}")
        # D4
        if isinstance(d4_voltage, float):
            d4_temp = voltage_to_temperature(d4_voltage)
            if d4_temp is not None:
                output_lines.append(f"  {d4_name}: {d4_voltage:.4f} V → {d4_temp:.3f} K")
            else:
                output_lines.append(f"  {d4_name}: {d4_voltage:.4f} V → None")
        else:
            output_lines.append(f"  {d4_name}: {d4_voltage}")
        # D5
        if isinstance(d5_voltage, float):
            d5_temp = voltage_to_temperature(d5_voltage)
            if d5_temp is not None:
                output_lines.append(f"  {d5_name}: {d5_voltage:.4f} V → {d5_temp:.3f} K")
            else:
                output_lines.append(f"  {d5_name}: {d5_voltage:.4f} V → None")
        else:
            output_lines.append(f"  {d5_name}: {d5_voltage}")

        self.temps_text.setText("\n".join(output_lines))

    def query_all_outputs(self):
        # Call OutputController.query_outputs for outputs 1-4 and display results in GUI only
        if OutputController:
            controller = OutputController()
            results = []
            for i in [1, 2, 3, 4]:
                results.append(f"Output {i}:")
                try:
                    response = controller.query_outputs(i, suppress_print=True)
                    results.append(str(response))
                except Exception as e:
                    results.append(f"Error querying output {i}: {e}")
                results.append("")
            self.output_text.setText("\n".join(results))
        else:
            self.output_text.setText("OutputController not found. Please check your imports.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
