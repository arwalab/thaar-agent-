from flask import Flask, request, jsonify
import os
import json
import uuid
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

# Optional: Load inventory data from Google Sheets
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit"
    ).worksheet("Food inventory")
    return sheet.get_all_records()

# Set up headless browser session
def attach_to_thaar_session():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    return webdriver.Chrome(options=chrome_options)

# Main automation logic
def add_to_cart_carrefour(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.carrefourksa.com/mafsau/en/")
        wait = WebDriverWait(driver, 20)

        try:
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='header_search__inp']"))
            )
        except Exception:
            print("⚠️ Search bar not found immediately. Checking overlays...")

            try:
                cookie_btn = driver.find_element(By.CSS_SELECTOR, "button#onetrust-accept-btn-handler")
                cookie_btn.click()
                print("✅ Cookie popup dismissed.")
            except:
                print("⚠️ No cookie banner.")

            try:
                lang_popup = driver.find_element(By.CSS_SELECTOR, ".languageSelectionContainer .closeBtn")
                lang_popup.click()
                print("✅ Language/location popup dismissed.")
            except:
                print("⚠️ No language popup.")

            # Retry
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='header_search__inp']"))
            )

        search_input.clear()
        search_input.send_keys(item_name)
        search_input.send_keys(Keys.RETURN)
        print(f"📦 Reordering: {item_name}")
        time.sleep(5)

    except Exception as e:
        screenshot_dir = "/app/failures"
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"{screenshot_dir}/error_{uuid.uuid4().hex}.png"
        driver.save_screenshot(filename)
        print(f"❌ Screenshot saved at: {filename}")
        raise Exception(f"Carrefour search bar not found (timeout or overlay issue): {e}")
    finally:
        driver.quit()

# API endpoint for reorder
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

# Start Flask server
def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
