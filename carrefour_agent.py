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

# Optional future: Load items from Google Sheets
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit").worksheet("Food inventory")
    return sheet.get_all_records()

def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    return webdriver.Chrome(options=chrome_options)

def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.carrefourksa.com/mafsau/en/")
        wait = WebDriverWait(driver, 20)

        # Wait for search bar to appear
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='header_search__inp']"))
        )

        search_input.clear()
        search_input.send_keys(item_name)
        search_input.send_keys(Keys.RETURN)

        print(f"📦 Reordering: {item_name}")
        time.sleep(5)  # optional: wait for results
    except Exception as e:
        # Dump page source for debugging
        with open("carrefour_error_dump.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise Exception(f"Carrefour search bar not found (timeout): {str(e)}")
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
        import traceback
        print("❌ Internal server error:", str(e))
        traceback.print_exc()  # 🔍 This will print full stack trace to Railway logs
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
