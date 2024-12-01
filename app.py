from fyers_apiv3 import fyersModel
import asyncio
import websockets
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import re
import math
import datetime
from flask import Flask, request, jsonify
import requests
import os


app = Flask(__name__)


ACCESS_TOKEN = os.environ.get("FYERS_ACCESS_TOKEN")
CLIENT_ID = os.environ.get("FYERS_CLIENT_ID")
  
# Initialize Fyers model
fyers = fyersModel.FyersModel(token=ACCESS_TOKEN, is_async=False, client_id=CLIENT_ID)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Parse JSON payload from TradingView
        data = request.json
        print("Webhook received:", data)

        # Extract necessary information
        action = data.get("action")
        symbol = data.get("symbol")
        price = data.get("price")
        quantity = data.get("quantity")

        # Validate the received data
        if not all([action, symbol, price, quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        # Call Fyers API to place the order
        fyers_response = place_order_fyers(action, symbol, quantity, price)
        return jsonify(fyers_response), 200

    except Exception as e:
        print("Error processing webhook:", str(e))
        return jsonify({"error": "Internal server error"}), 500
        
def place_order_fyers(action, symbol, quantity, price):
    try:
        # Prepare the order payload       
        order_data = {     
        "symbol": symbol, "qty": quantity, "type": 1, "side": 1 if action == "buy" else -1, 
        "productType": "MARGIN", "limitPrice": price, "stopPrice": 0, "validity": "DAY",
        "stopLoss": 0, "takeProfit": 0, "offlineOrder": False, "disclosedQty": 0
        }

        # Place the order using Fyers API
        response = fyers.place_order(order_data)

        # Handle response
        if response["code"] == 200:
            return {"status": "success", "data": response}
        else:
            return {"status": "failure", "message": response.get("message", "Unknown error")}

    except Exception as e:
        print("Error placing order:", str(e))
        return {"status": "failure", "message": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)    