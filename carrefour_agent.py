from flask import Flask, request, jsonify
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ✅ Launch Chrome with ThaarSession and remote debugging (must be running)
DEBUGGING_URL = "http://127.0.0.1:9222"

# ✅ Helper to connect to the existing Chrome session via remote debugging
def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# ✅ Search and add product to cart on Carrefour
def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    driver.get("https://www.carrefourksa.com/mafsau/en/")

    wait = WebDriverWait(driver, 15)
    print("⏳ Waiting for search bar...")

    try:
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        search_box.clear()
        search_box.send_keys(item_name)
        search_box.send_keys(Keys.RETURN)

        print(f"🔍 Searched: {item_name}")

        product = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tile-container, div.product-list__item")))
        print(f"✅ Found product: {item_name}")

        add_button = product.find_element(By.XPATH, ".//button[contains(., 'Add') or contains(., 'Add to Cart')]")
        add_button.click()

        print(f"🛒 Clicked 'Add to cart' for: {item_name}")
    except Exception as e:
        print(f"❌ Failed to add {item_name} to cart: {e}")
    finally:
        driver.quit()

@app.route("/reorder", methods=["POST"])
def reorder_item():
    data = request.get_json(force=True)
    print("✅ Raw request data:", data)

    items = data.get("item")
    if not items:
        return jsonify({"error": "Missing 'item' in request"}), 400

    if isinstance(items, str):
        items = [items]

    print("🛒 Items received:", items)

    for item in items:
        print(f"\n📦 Reordering: {item}")
        add_to_cart_carrefour(item)

    return jsonify({"items": items, "status": "success"}), 200

def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Thaar is live at http://0.0.0.0:{port}\n")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
