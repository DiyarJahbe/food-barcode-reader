import sys
import cv2
import requests
import pygame
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer

# Path to beep sound file
SOUND_PATH = "beep-06.wav"

# Initialize pygame for sound
pygame.mixer.init()

def play_sound():
    """Plays a beep sound when a barcode is detected."""
    pygame.mixer.music.load(SOUND_PATH)
    pygame.mixer.music.play()

# Open Food Facts API
OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/product/"

class BarcodeScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle("Barcode Scanner & Nutrition Analyzer")
        self.setGeometry(200, 200, 800, 600)
        
        # Video display
        self.video_label = QLabel(self)
        
        # Diet selection dropdown
        self.diet_label = QLabel("Select your diet:")
        self.diet_dropdown = QComboBox(self)
        self.diet_dropdown.addItems(["Keto", "Bodybuilding", "Losing Weight"])
        
        # Scan button
        self.scan_button = QPushButton("Start Scanning", self)
        self.scan_button.clicked.connect(self.start_scanning)
        
        # Table for results
        self.result_table = QTableWidget(5, 2, self)
        self.result_table.setHorizontalHeaderLabels(["Nutrient", "Amount (g)"])
        self.result_table.setVerticalHeaderLabels(["Energy", "Fat", "Carbohydrates", "Protein", "Sugars"])
        
        # Diet advice label
        self.advice_label = QLabel("Diet Advice:")
        self.advice_text = QTextEdit(self)
        self.advice_text.setReadOnly(True)
        
        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.diet_label)
        layout.addWidget(self.diet_dropdown)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.result_table)
        layout.addWidget(self.advice_label)
        layout.addWidget(self.advice_text)
        
        self.setLayout(layout)

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_barcodes = decode(gray, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128])
            
            if detected_barcodes:
                for barcode in detected_barcodes:
                    barcode_data = barcode.data.decode("utf-8")
                    play_sound()
                    self.get_nutrition(barcode_data)
                    self.timer.stop()
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def get_nutrition(self, barcode):
        response = requests.get(f"{OFF_SEARCH_URL}{barcode}.json")
        if response.status_code == 200:
            data = response.json()
            if "product" in data:
                product = data["product"]
                product_name = product.get("product_name", "Unknown")
                nutrients = {
                    "Energy": product.get("nutriments", {}).get("energy-kcal", 0),
                    "Fat": product.get("nutriments", {}).get("fat", 0),
                    "Carbohydrates": product.get("nutriments", {}).get("carbohydrates", 0),
                    "Protein": product.get("nutriments", {}).get("proteins", 0),
                    "Sugars": product.get("nutriments", {}).get("sugars", 0),
                }
                
                for row, (key, value) in enumerate(nutrients.items()):
                    self.result_table.setItem(row, 0, QTableWidgetItem(key))
                    self.result_table.setItem(row, 1, QTableWidgetItem(str(value)))
                
                diet_type = self.diet_dropdown.currentText().lower()
                diet_advice = self.give_diet_advice(diet_type, nutrients, product_name)
                self.advice_text.setText(diet_advice)
            else:
                self.advice_text.setText("No nutritional data found for this barcode.")
        else:
            self.advice_text.setText("Error fetching data from Open Food Facts API.")

    def give_diet_advice(self, diet_type, nutrients, product_name):
        calories = nutrients["Energy"]
        sugar = nutrients["Sugars"]
        protein = nutrients["Protein"]
        carbs = nutrients["Carbohydrates"]
        
        if diet_type == "keto":
            return f"⚡ Keto: Avoid sugar, focus on fats. {carbs}g carbs & {sugar}g sugar." + (" ✅ OK" if carbs < 10 and sugar < 5 else " ❌ Not Keto!")
        elif diet_type == "bodybuilding":
            return f"🏋️ Bodybuilding: High protein needed. {protein}g protein & {calories} kcal." + (" ✅ Good choice!" if protein > 10 else " ❌ Low protein!")
        elif diet_type == "losing weight":
            return f"🏃 Weight Loss: Keep it low-calorie. {calories} kcal & {sugar}g sugar." + (" ✅ Suitable!" if calories < 200 and sugar < 5 else " ❌ Too high!")
        return "⚠️ Unknown diet type."

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
