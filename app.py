import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the access token and verify token from environment variables
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/", methods=["GET", "POST"])
def webhook():
    # Log the entire incoming request for debugging
    print(f"Request headers: {request.headers}")
    print(f"Request args: {request.args}")
    
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        mode = request.args.get("hub.mode")

        print(f"Verification token: {verify_token}")
        print(f"Challenge: {challenge}")
        print(f"Mode: {mode}")
        
        # Check if the verify_token matches
        if mode == "subscribe" and verify_token == VERIFY_TOKEN:
            return challenge  # Respond with the challenge value
        else:
            print("Token mismatch, verification failed!")
            return "Invalid verification token", 403

        return "Invalid method", 405

    elif request.method == "POST":
        # This handles the POST requests from Facebook with messages
        data = request.json
        print(f"Received POST request: {data}")
        if data.get("object") == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    sender_id = messaging_event["sender"]["id"]  # User ID
                    message = messaging_event.get("message", {}).get("text")  # User's message
                    if message:
                        # Call function to send a response
                        send_message(sender_id, "You said: " + message)
        return "OK", 200

def send_message(recipient_id, message_text):
    url = f'https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Message sent: {response.status_code}")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
