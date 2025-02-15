import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import requests
import pygame

# Path to beep sound file
SOUND_PATH = r"beep-06.wav"

# Initialize pygame for sound
pygame.mixer.init()

def play_sound():
    """Plays a beep sound when a barcode is detected."""
    pygame.mixer.music.load(SOUND_PATH)
    pygame.mixer.music.play()

# Open Food Facts API
OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/product/"

def get_nutrition(barcode):
    """Fetches nutrition details from Open Food Facts API and provides dietary instructions."""
    response = requests.get(f"{OFF_SEARCH_URL}{barcode}.json")
    if response.status_code == 200:
        data = response.json()
        if "product" in data:
            product = data["product"]
            print(f"\n📦 Product: {product.get('product_name', 'Unknown')}")
            nutrients = {
                "Energy": product.get("nutriments", {}).get("energy-kcal", 0),
                "Fat": product.get("nutriments", {}).get("fat", 0),
                "Carbohydrates": product.get("nutriments", {}).get("carbohydrates", 0),
                "Protein": product.get("nutriments", {}).get("proteins", 0),
                "Sugars": product.get("nutriments", {}).get("sugars", 0),
            }

            # Ensure all values are floats for comparison
            for key, value in nutrients.items():
                if isinstance(value, str):  # In case of string values like "N/A"
                    nutrients[key] = 0 if value == 'N/A' else float(value)
                print(f"{key}: {nutrients[key]}g")

            # Ask user for diet type
            diet_type = input("\nWhat diet are you following? (keto/bodybuilding/losing weight): ").strip().lower()
            give_diet_advice(diet_type, nutrients, product.get("product_name", "this product"))
        else:
            print("No nutritional data found for this barcode.")
    else:
        print("Error fetching data from Open Food Facts API.")

def give_diet_advice(diet_type, nutrients, product_name):
    """Analyzes the product based on the selected diet and provides specific instructions."""
    calories = nutrients["Energy"]
    sugar = nutrients["Sugars"]
    protein = nutrients["Protein"]
    carbs = nutrients["Carbohydrates"]
    fat = nutrients["Fat"]

    print("\n📌 Diet Instructions:")

    if diet_type == "keto":
        print(f"⚡ **Keto Diet Advice for {product_name}:**")
        print("- High fat, moderate protein, very low carbs.")
        print("- **Avoid sugar** and high-carb products.")
        print(f"- This product contains {carbs}g carbs, {sugar}g sugar, and {calories} kcal.")

        if carbs < 10 and sugar < 5:
            print("✅ **Suitable for keto!** You can eat this in moderation.")
            daily_limit = 1  # Serving size per day for Keto
            print(f"👉 **You can eat up to {daily_limit} serving per day** to stay within keto macros.")
        else:
            print("❌ **Not keto-friendly!** Try a low-carb alternative.")
            print("👉 **If you really want to eat it, only 1 small piece is recommended to not exceed your carb limits.**")
            print("👉 **Try low-carb snacks like a protein bar or cheese.**")

    elif diet_type == "bodybuilding":
        print(f"🏋️ **Bodybuilding Advice for {product_name}:**")
        print("- High protein intake for muscle growth.")
        print("- Moderate carbs for energy and muscle recovery.")
        print(f"- This product contains {protein}g protein and {calories} kcal.")

        daily_protein_goal = 150  # Example: daily protein goal for bodybuilding
        servings_needed = daily_protein_goal / protein
        servings_needed = round(servings_needed, 1) if protein > 0 else "N/A"
        
        if protein > 10:
            print("✅ **Good for muscle building!**")
            print(f"👉 **To meet your daily protein goal of {daily_protein_goal}g, consume {servings_needed} servings.**")
            print("- Best to eat **before or after workouts** for muscle recovery.")
        else:
            print("⚠️ **Low in protein!** Consider a protein shake or higher-protein option.")
            print("👉 **Try higher-protein alternatives like chicken breast or a protein shake.**")
            print("👉 **If you really want to eat it, you can have 1 piece but make sure to supplement with a protein shake.**")

    elif diet_type == "losing weight":
        print(f"🏃 **Weight Loss Advice for {product_name}:**")
        print("- Focus on **low-calorie, high-protein, and fiber-rich foods**.")
        print(f"- This product contains {calories} kcal and {sugar}g sugar.")

        daily_calorie_limit = 2000  # Example: daily calorie limit for weight loss
        daily_sugar_limit = 25  # Example: daily sugar limit for weight loss
        daily_servings = daily_calorie_limit / calories  # Calculate servings for the daily limit

        if calories < 200 and sugar < 5:
            print("✅ **Good for weight loss!**")
            print(f"👉 **You can consume up to {round(daily_servings, 1)} servings per day**.")
        else:
            print("❌ **Too high in calories or sugar!** Consider a lower-calorie alternative.")
            print("👉 **If you want to eat it, only 1 small piece is recommended to avoid exceeding your calorie intake.**")
            print("👉 **Try lower-calorie alternatives like fruits, veggies, or protein bars.**")

    else:
        print("⚠️ **Unknown diet type.** Please enter a valid diet (keto, bodybuilding, losing weight).")

# Initialize webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    # Flip image like a mirror
    img = cv2.flip(img, 1)

    # Convert to grayscale for better barcode detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Decode only EAN-13 and CODE128 barcodes
    detectedBarcodes = decode(gray, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128])

    if detectedBarcodes:
        for barcode in detectedBarcodes:
            barcode_data = barcode.data.decode("utf-8")
            print(f"\n✅ **Barcode Detected:** {barcode_data}")

            # Play sound when a barcode is detected
            play_sound()

            # Fetch and print nutrition details
            get_nutrition(barcode_data)

            # Release resources and exit
            cap.release()
            cv2.destroyAllWindows()
            exit()
    
    cv2.imshow('Barcode Scanner', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# End of main.py