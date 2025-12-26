# Get Discord Token From Browser

Guide on how to get your Discord token from the browser console and a Python example for sending messages.

## How to Get Your Discord Token

### New Method

1. Open the browser console with `F12` or `Ctrl + Shift + I`.
2. Enable mobile device emulation with `Ctrl + Shift + M`.
3. Paste the following code into the console and press Enter:

```javascript
const iframe = document.createElement('iframe');
console.log(
  'Token: %c%s',
  'font-size:16px;',
  JSON.parse(document.body.appendChild(iframe).contentWindow.localStorage.token)
);
iframe.remove();
```

Alternatively, you can just go to the **Application** tab, then **Local Storage**, and find the `token` key under `https://discord.com/` after you have enabled mobile device emulation.

### Old Method

1. Open the browser console with `F12` or `Ctrl + Shift + I`.
2. Go to the **Network** tab
3. Filter by **Fetch/XHR**
4. Choose a request that isn't an error (if there aren't any, click on a channel or server to trigger some requests.)
5. You'll find your discord token under the request headers -> **authorization** section. Copy and paste it from there.

## Python Example: Sending a Message

Here's a simple Python example of how to send a message to a Discord channel using your token:

```python
import requests

def send_discord_message(token, channel_id, message):
    """
    Send a message to a Discord channel using your user token.
    
    Args:
        token: Your Discord token
        channel_id: The ID of the channel to send the message to
        message: The message content to send
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    
    data = {
        "content": message
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("Message sent successfully!")
            return True
        else:
            print(f"Failed to send message. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Replace these with your actual values
    DISCORD_TOKEN = "YOUR_DISCORD_TOKEN_HERE"
    CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"
    MESSAGE = "Hello from Python! 👋"
    
    send_discord_message(DISCORD_TOKEN, CHANNEL_ID, MESSAGE)
```

## Getting Channel ID

To get a channel ID:

1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)
2. Right-click on the channel you want to send messages to
3. Click "Copy ID"

## Installation

Install the required Python package:

```bash
pip install requests
```

## Discord Webhook: Order Embed Example

Here's an example of how to send a styled embed message (like order notifications) using Discord webhooks:

```python
import requests
import json
from datetime import datetime

def send_order_webhook(webhook_url, order_data):
    """Send a Discord webhook message with an order embed."""
    
    embed = {
        "title": "✅ New Completed Order",
        "color": 0xFF69B4,  # Pink color
        "fields": [
            {
                "name": "👤 User",
                "value": f"🔒 {order_data.get('user', 'Hidden')}",
                "inline": True
            },
            {
                "name": "💳 Payment Method",
                "value": f"💳 {order_data.get('payment_method', 'Credit/Debit Card')}",
                "inline": True
            },
            {
                "name": "🪙 Robux Purchased",
                "value": order_data.get('robux_amount', '0 Robux'),
                "inline": True
            },
            {
                "name": "💰 USD Spent",
                "value": order_data.get('usd_amount', '$0.00'),
                "inline": True
            },
            {
                "name": "⭐ Rating",
                "value": "⭐⭐⭐⭐⭐ " + f"({order_data.get('rating', '5/5')})",
                "inline": True
            },
            {
                "name": "📄 Order ID",
                "value": order_data.get('order_id', 'N/A'),
                "inline": True
            }
        ],
        "thumbnail": {
            "url": order_data.get('thumbnail_url', '')
        },
        "footer": {
            "text": f"Powered by Robux World • discord.gg/robuxworld • {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {"embeds": [embed]}
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 204

# Usage
WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
order_data = {
    "user": "Hidden",
    "payment_method": "Giftcards",
    "robux_amount": "30,000 Robux",
    "usd_amount": "$30.00",
    "rating": "5/5",
    "order_id": "0094825791242530142",
    "thumbnail_url": "https://i.imgur.com/your-logo.png"
}

send_order_webhook(WEBHOOK_URL, order_data)
```

### Getting a Webhook URL

1. Go to your Discord server
2. Go to Server Settings > Integrations > Webhooks
3. Click "New Webhook"
4. Configure the webhook (name, channel, etc.)
5. Copy the webhook URL

## Important Notes

⚠️ **Warning**: Using your Discord token to automate messages violates Discord's Terms of Service. Use at your own risk. Discord may ban your account if detected.

- Never share your Discord token or webhook URL publicly
- Keep your tokens and webhooks secure
- This is for educational purposes only
