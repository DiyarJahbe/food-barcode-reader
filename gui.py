import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from backend import fetch_nutrition, process_frame

class BarcodeScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle("Barcode Scanner & Nutrition Analyzer")
        self.setGeometry(200, 200, 900, 600)
        
        # Camera display
        self.video_label = QLabel(self)

        # Diet selection
        self.diet_label = QLabel("Select your diet:")
        self.diet_dropdown = QComboBox(self)
        self.diet_dropdown.addItems(["Keto", "Bodybuilding", "Losing Weight"])

        # Scan button
        self.scan_button = QPushButton("Start Scanning", self)
        self.scan_button.clicked.connect(self.start_scanning)

        # Nutrition table
        self.result_table = QTableWidget(9, 2, self)
        self.result_table.setHorizontalHeaderLabels(["Nutrients", "Amount"])

        # Advice text
        self.advice_label = QLabel("Advice:")
        self.advice_text = QTextEdit(self)
        self.advice_text.setReadOnly(True)

        # Layout
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        left_layout.addWidget(self.video_label)
        left_layout.addWidget(self.diet_label)
        left_layout.addWidget(self.diet_dropdown)
        left_layout.addWidget(self.scan_button)

        right_layout.addWidget(self.result_table)
        right_layout.addWidget(self.advice_label)
        right_layout.addWidget(self.advice_text)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            barcode_data = process_frame(frame)

            if barcode_data:
                self.display_nutrition(barcode_data)
                self.timer.stop()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def display_nutrition(self, barcode):
        """Fetches and displays product details based on barcode and selected diet."""
        diet_type = self.diet_dropdown.currentText().lower()  # Get selected diet
        product_data = fetch_nutrition(barcode)

        if product_data:
            # Insert product details
            self.result_table.setItem(0, 0, QTableWidgetItem("Product"))
            self.result_table.setItem(0, 1, QTableWidgetItem(product_data['name']))
            
            self.result_table.setItem(1, 0, QTableWidgetItem("Brand"))
            self.result_table.setItem(1, 1, QTableWidgetItem(product_data['brand']))

            # Display nutrients
            nutrients = product_data["nutrients"]
            for row, (key, value) in enumerate(nutrients.items(), start=2):
                self.result_table.setItem(row, 0, QTableWidgetItem(key))
                self.result_table.setItem(row, 1, QTableWidgetItem(str(value)))

            # Generate diet advice
            calories = nutrients.get("Energy (kcal)", 0)
            protein = nutrients.get("Protein (g)", 0)
            sugar = nutrients.get("Sugars (g)", 0)
            carbs = nutrients.get("Carbohydrates (g)", 0)

            advice = "⚠️ No specific advice available."

            if diet_type == "keto":
                if carbs < 10 and sugar < 5:
                    advice = "✅ Suitable for keto! You can eat this in moderation."
                else:
                    advice = "❌ High in carbs! Limit intake to a small portion."

            elif diet_type == "bodybuilding":
                if protein > 10:
                    advice = "💪 High in protein! Good for muscle growth."
                else:
                    advice = "⚠️ Low in protein! Consider adding a protein shake."

            elif diet_type == "losing weight":
                if calories < 200 and sugar < 5:
                    advice = "🏃 Low-calorie option! Good for weight loss."
                else:
                    advice = "❌ High in calories! Eat only a small portion."

            self.advice_text.setText(advice)  # ✅ Display advice

        else:
            self.advice_text.setText("No product data found for this barcode.")

    def start_scanning(self):
        self.timer.start(30)

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeScannerApp()
    window.show()
    sys.exit(app.exec_())
