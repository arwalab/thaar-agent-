from flask import Flask, request, jsonify
import os
import json
import tempfile
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
    # Uncomment for debugging locally:
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    # Add a unique user data dir to prevent session reuse issues
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_google_search(item_name):
    driver = attach_to_thaar_session()
    try:
        driver.get("https://www.google.com")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "q"))
        )

        search = driver.find_element(By.NAME, "q")
        search.send_keys(item_name)
        search.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3"))
        )
        first_result = driver.find_element(By.CSS_SELECTOR, "h3").text
        print(f"🔍 First search result for '{item_name}': {first_result}", flush=True)

        # Save a screenshot for debugging in headless mode
        screenshot_path = f"/tmp/{item_name.replace(' ', '_')}_search.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}", flush=True)

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
        test_google_search(item)
        return jsonify({"item": item, "status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
