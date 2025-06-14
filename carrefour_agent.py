from flask import Flask, request, jsonify
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

app = Flask(__name__)

# --------------------------
# 🔐 Google Sheets Function
# --------------------------
def load_items_from_sheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1qhPYmOREyR8ShPJbMAxmvzD96cVluToZ5iLA94KxHng/edit"
    ).worksheet("Food inventory")
    return sheet.get_all_records()

# --------------------------
# 🚚 API Endpoint for Reorder
# --------------------------
@app.route("/reorder", methods=["POST"])
def reorder_item():
    try:
        data = request.get_json(force=True)
        print("\n✅ Raw request data:", data)

        item = data.get("item")
        if not item:
            return jsonify({"error": "Missing 'item' in request"}), 400

        print(f"🛒 Item received: {item}")
        # Optionally you could perform product lookup, automation, etc.

        return jsonify({"item": item, "status": "success"}), 200

    except Exception as e:
        print("❌ Error processing request:", str(e))
        return jsonify({"error": str(e)}), 500

# --------------------------
# 🚀 Launch Flask App
# --------------------------
def main():
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Thaar is live at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
