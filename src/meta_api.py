import os

import requests
from dotenv import load_dotenv

load_dotenv("../secrets.env")

WHATSAPP_NUMBER_ID = os.getenv("WHATSAPP_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")


def respondWhatsapp(clientNumber, message):
    url = f"https://graph.facebook.com/v15.0/{WHATSAPP_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    json = {
        "messaging_product": "whatsapp",
        "to": str(clientNumber),
        "text": {"body": str(message)},
    }

    req = requests.post(url, headers=headers, json=json)
    print(req.text)


def respondMessenger(PSID, message):
    print("message before", message)
    # message = message.encode("UTF-8", "ignore")
    # print("message after", message)
    url = (
        f"https://graph.facebook.com/v15.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    )
    json = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": str(PSID)},
        "message": {"text": message},
    }

    req = requests.post(url, json=json)
    print(req.text)
