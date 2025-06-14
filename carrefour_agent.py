from flask import Flask, request, jsonify
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

# 🧠 Google Sheets connection
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit").worksheet("Food inventory")
    data = sheet.get_all_records()
    return data

# 🧭 Attach to browser session (headless Chrome on Railway)
def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)
    return driver

# 🛒 Automate Carrefour add-to-cart
def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.carrefourksa.com/mafsau/en/")
        time.sleep(3)

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(item_name)
        search_box.submit()
        time.sleep(5)

        # Try clicking first 'Add to cart' button (if found)
        add_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Add to cart')]")
        if add_buttons:
            add_buttons[0].click()
            print(f"🛒 Successfully added {item_name} to cart.")
        else:
            print(f"⚠️ No add button found for {item_name}")
    except Exception as e:
        print(f"❌ Error during Carrefour automation: {e}")
    finally:
        driver.quit()

# 🧩 Endpoint
@app.route("/reorder", methods=["POST"])
def reorder_item():
    data = request.get_json(force=True)
    print("✅ Raw request data:", data)
    items = data.get("item")

    if not items:
        return jsonify({"error": "Missing 'item' in request"}), 400

    if isinstance(items, str):
        items = [items]

    print(f"🛒 Items received: {items}")
    for item in items:
        print(f"📦 Reordering: {item}")
        add_to_cart_carrefour(item)

    return jsonify({"status": "success", "items": items}), 200

# 🚀 Launch
def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
