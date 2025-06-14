from flask import Flask, request, jsonify
import os
import json
import gspread
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Optional: connect to Google Sheet
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit").worksheet("Food inventory")
    return sheet.get_all_records()

# Attach to headless Chrome (on Railway)
def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Automate Carrefour search
def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.carrefourksa.com/mafsau/en/")
        print("🌐 Opened Carrefour")

        # Wait for search bar using ID
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "search-bar"))
        )
        search = driver.find_element(By.ID, "search-bar")
        search.send_keys(item_name)
        search.send_keys(Keys.RETURN)
        print(f"📦 Reordering: {item_name}")
        time.sleep(5)

    except TimeoutException:
        print("❌ Timeout: Could not find the search bar.")
        raise Exception("Carrefour search bar not found (timeout)")

    except WebDriverException as e:
        print(f"❌ WebDriver crashed: {e}")
        raise Exception(f"WebDriver error: {str(e)}")

    finally:
        driver.quit()

# Endpoint to receive reorder request
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

# Entry point for Railway
def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
