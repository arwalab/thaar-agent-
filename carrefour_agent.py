from flask import Flask, request, jsonify
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)

# 🧠 Helper: Attach to browser in Railway or headless
def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"  # for Railway
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 🛒 Logic: Add an item to Carrefour cart
def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()

    print(f"🌐 Opening Carrefour website...")
    driver.get("https://www.carrefourksa.com/mafksa/en/")

    time.sleep(5)  # Wait for page load

    print(f"🔎 Searching for: {item_name}")
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(item_name)
    search_box.submit()

    time.sleep(5)  # Wait for search results

    try:
        print("➕ Attempting to add first item to cart...")
        add_btn = driver.find_element(By.XPATH, '//button[contains(., "Add to cart")]')
        add_btn.click()
        print("✅ Item added to cart.")
    except Exception as e:
        print("❌ Failed to add item:", e)

    driver.quit()

# 🔗 API endpoint
@app.route("/reorder", methods=["POST"])
def reorder_item():
    data = request.get_json(force=True)
    print("✅ Raw request data:", data)

    item = data.get("item")
    if not item:
        return jsonify({"status": "error", "message": "Missing item name"}), 400

    print(f"🛒 Items received: [{item}]")
    print(f"📦 Reordering: {item}")

    try:
        add_to_cart_carrefour(item)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"item": item, "status": "success"}), 200

# 🔁 Main server start
def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Thaar is live at http://0.0.0.0:{port}\n")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
