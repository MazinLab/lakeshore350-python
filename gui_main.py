
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel

# Import your output querying logic
try:
    from lakeshore350.outputs import OutputController
except ImportError:
    OutputController = None  # Fallback for initial scaffold

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lakeshore 350 Controller")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        layout = QVBoxLayout()

        self.info_label = QLabel("Lakeshore 350 GUI")
        layout.addWidget(self.info_label)

        self.query_button = QPushButton("Query Outputs")
        self.query_button.clicked.connect(self.query_all_outputs)
        layout.addWidget(self.query_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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
