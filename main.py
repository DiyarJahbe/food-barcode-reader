import cv2
from pyzbar.pyzbar import decode
import requests
import time

# Using Open Food Facts API (Free & Public)
OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/product/"

def get_nutrition(barcode):
    response = requests.get(f"{OFF_SEARCH_URL}{barcode}.json")
    if response.status_code == 200:
        data = response.json()
        if "product" in data:
            product = data["product"]
            print(f"Product: {product.get('product_name', 'Unknown')}")
            nutrients = {
                "Energy": product.get("nutriments", {}).get("energy-kcal", "N/A"),
                "Fat": product.get("nutriments", {}).get("fat", "N/A"),
                "Carbohydrates": product.get("nutriments", {}).get("carbohydrates", "N/A"),
                "Protein": product.get("nutriments", {}).get("proteins", "N/A"),
            }
            for key, value in nutrients.items():
                print(f"{key}: {value}")
        else:
            print("No nutritional data found for this barcode.")
    else:
        print("Error fetching data from Open Food Facts API.")

# Initialize webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    # Flip the image like a mirror
    img = cv2.flip(img, 1)
    detectedBarcodes = decode(img)

    if detectedBarcodes:
        for barcode in detectedBarcodes:
            barcode_data = barcode.data.decode("utf-8")
            print(f"Barcode Detected: {barcode_data}")
            get_nutrition(barcode_data)
            cap.release()
            cv2.destroyAllWindows()
            exit()
    
    cv2.imshow('Barcode Scanner', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
