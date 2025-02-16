import requests
import pygame
from pyzbar.pyzbar import decode, ZBarSymbol
import cv2

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

def fetch_nutrition(barcode):
    response = requests.get(f"{OFF_SEARCH_URL}{barcode}.json")
    if response.status_code == 200:
        data = response.json()
        if "product" in data:
            product = data["product"]
            return {
                "name": product.get("product_name", "Unknown"),
                "brand": product.get("brands", "Unknown"),
                "nutrients": {
                    "Energy (kcal)": product.get("nutriments", {}).get("energy-kcal", 0),
                    "Fat (g)": product.get("nutriments", {}).get("fat", 0),
                    "Saturated Fat (g)": product.get("nutriments", {}).get("saturated-fat", 0),
                    "Carbohydrates (g)": product.get("nutriments", {}).get("carbohydrates", 0),
                    "Sugars (g)": product.get("nutriments", {}).get("sugars", 0),
                    "Protein (g)": product.get("nutriments", {}).get("proteins", 0),
                    "Salt (g)": product.get("nutriments", {}).get("salt", 0),
                }
            }
    return None

def process_frame(frame):
    """Processes a frame and detects barcodes."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_barcodes = decode(gray, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128])

    if detected_barcodes:
        for barcode in detected_barcodes:
            barcode_data = barcode.data.decode("utf-8")
            play_sound()
            return barcode_data
    return None
