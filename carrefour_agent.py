# ✅ Updated carrefour_agent.py to support batch item processing (for Railway deployment)

from flask import Flask, request, jsonify
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

app = Flask(__name__)

# Load item list from Google Sheets
def load_items_from_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit").worksheet("Food inventory")
    return sheet.get_all_records()

@app.route("/reorder", methods=["POST"])
def reorder_items():
    data = request.get_json(force=True)
    print("✅ Raw request data:", data)

    if isinstance(data, dict):
        # Single item case
        items = [data.get("item")]
    elif isinstance(data, list):
        # List of items
        items = [entry.get("item") for entry in data if "item" in entry]
    else:
        return jsonify({"error": "Invalid request format"}), 400

    print("🛒 Items received:", items)
    
    results = []
    for item in items:
        if item:
            # Simulate a reorder operation
            print(f"📦 Reordering: {item}")
            results.append({"item": item, "status": "success"})
        else:
            results.append({"item": None, "status": "skipped - no item"})

    return jsonify(results), 200

# Entrypoint
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Thaar is live at http://0.0.0.0:{port}\n")
    app.run(host="0.0.0.0", port=port)
