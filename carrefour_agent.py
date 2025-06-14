from flask import Flask, request, jsonify
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Google Sheets setup (optional for future enhancements)
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit").worksheet("Food inventory")
    data = sheet.get_all_records()
    return data

def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.carrefourksa.com/mafsau/en/")

        # Ensure cookie popup is dismissed before proceeding
        try:
            print("🧼 Checking for cookie overlay...", flush=True)
            accept_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']"))
            )
            accept_button.click()
            print("🍪 Cookie popup closed.", flush=True)
            time.sleep(2)
        except:
            print("⚠️ No cookie popup found or already dismissed.", flush=True)

        # Wait for body and scroll to trigger JS loading
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 500);")
        print("⏳ Page body and scroll loaded", flush=True)

        # Wait for search bar
        try:
            print("🔎 Waiting for search bar...", flush=True)
            search = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='header_search__inp']"))
            )
            search.send_keys(item_name)
            search.send_keys(Keys.RETURN)
            print(f"📦 Reordering: {item_name}", flush=True)
            time.sleep(5)
        except Exception as e:
            raise Exception("Carrefour search bar not found (timeout or overlay issue): " + str(e))

    finally:
        driver.quit()

@app.route("/reorder", methods=["POST"])
def reorder_item():
    try:
        data = request.get_json(force=True)
        print("✅ Raw request data:", data)
        item = data.get("item")
        if not item:
            return jsonify({"error": "Missing 'item' in request"}), 400

        print(f"🛒 Items received: {[item]}")
        add_to_cart_carrefour(item)
        return jsonify({"item": item, "status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
