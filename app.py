import json
from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Your Facebook Page Access Token and Verify Token
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# Load the knowledge base
with open("knowledge_base.json", "r") as f:
    knowledge_base = json.load(f)

# Function to send a message
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v13.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

# Webhook to handle messages
@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.json
    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                sender_id = event["sender"]["id"]
                if "message" in event:
                    user_message = event["message"].get("text")
                    if user_message:
                        # Search knowledge base for a response
                        response = knowledge_base.get(
                            user_message.lower(),
                            "Sorry, I don't have an answer to that."
                        )
                        send_message(sender_id, response)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=10000)
