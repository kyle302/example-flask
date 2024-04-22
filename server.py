from flask import Flask, request, jsonify
import requests
import json
import telegrambot
from tabulate import tabulate

app = Flask('')

def map_timeframe_to_resolution(timeframe):
    # Check if the timeframe is one of 'D', 'W', 'M'
    if timeframe in ['D', 'W', 'M']:
        return timeframe
    else:
        # Extract the numeric part from the timeframe
        # Assuming the format is like 'H1', 'H4', 'M30', etc.
        numeric_part = ''.join(filter(str.isdigit, timeframe))
        return numeric_part

def format_message(data, api_response_data):
    item = data.get("data", [{}])[0]

    # Primary signal generation table
    primary_table_data = [
        ["Symbol", item.get("symbol", "N/A")],
        ["Timeframe", item.get("timeframe", "N/A")],
        ["Direction", "Bearish" if item.get("patterntype", "").lower() == "bearish" else "Bullish"],
        ["Pattern Name", item.get("patternname", "N/A")],
        ["Entry Price", item.get("entry", "N/A").split("_")[0]],
        ["TP1", item.get("profit1", "N/A")],
        ["TP2", item.get("profit2", "N/A")],
        ["SL", item.get("stoploss", "N/A")]
    ]
    primary_message = tabulate(primary_table_data, tablefmt="fancy_grid", headers=["Field", "Value"])

    # Technical Analysis table
    technical_analysis_data = api_response_data.get('technicalAnalysis', {})
    signal = technical_analysis_data.get('signal', 'N/A')  # Correctly access the signal
    trend_data = api_response_data.get('trend', {})
    trending = trend_data.get('trending', 'N/A')  # Correctly access the trending value
    technical_table_data = [
        ["Signal", signal],
        ["Trending", str(trending)]  # Ensure boolean values are converted to string
    ]
    technical_message = tabulate(technical_table_data, tablefmt="fancy_grid", headers=["Technical Analysis"])

    # Combine both messages
    message = f"{primary_message}\n\n{technical_message}"
    return message

@app.route('/webhook', methods=['POST'])
def post_message():
    try:
        jsonPayload = json.loads(request.data.decode('utf-8'))
        if jsonPayload:
            # Extract symbol and timeframe for API call
            item = jsonPayload.get("data", [{}])[0]
            symbol = item.get('symbol')
            timeframe = item.get('timeframe', 'H1')  # Default to H1 if not provided

            # Apply the correct prefix based on the symbol
            if "BTC/USDT" in symbol:
                symbol = "BINANCE:BTCUSDT"
            elif "/" in symbol:  # Assuming forex pairs contain a slash
                symbol = f"OANDA:{symbol.replace('/', '_')}"
            else:
                # Adjust symbol formatting if necessary for other cases
                symbol = symbol.replace("/", "_")

            # Map timeframe to resolution
            resolution = map_timeframe_to_resolution(timeframe)

            # Construct the API URL
            api_url = f"https://harmonicpattern.com/api/v1/scan/technical-indicator?symbol={symbol}&resolution={resolution}&token=ckaeej5mp9p5kk4lcfr0"

            # Print the API call URL for debugging
            print(f"Making API call to URL: {api_url}")

            # Make the API call
            response = requests.get(api_url)
            if response.status_code == 200:
                # Process the API response
                api_response_data = response.json()

                # Print the API response data to the console for debugging
                print("API Response Data:", api_response_data)

                # Format the message
                formatted_message = format_message(jsonPayload, api_response_data)

                # Send the formatted message via Telegram bot
                telegrambot.sendMessage(formatted_message)  # Ensure you have a function or method `sendMessage` correctly implemented in `telegrambot`

                return 'success', 200
            else:
                print(f"API call failed: {response.status_code}")
                return 'API call failed', 500
        else:
            return 'No JSON payload received.', 400
    except Exception as e:
        print(f"[X] Exception Occurred: {e}")
        return 'failure', 500

@app.route('/')
def main():
    return 'Your bot is alive!'

def run():
    app.run(host='0.0.0.0', port=5000)

def start_server_async():
    server = Thread(target=run)
    server.start()

def start_server():
    app.run(host='0.0.0.0', port=5000)