# Discord Message Bot

A simple Python script to send messages to Discord channels using your Discord token.

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

## Requirements

```bash
pip install requests
```

## Important Notes

⚠️ **Warning**: Using your Discord token to automate messages violates Discord's Terms of Service. Use at your own risk. Discord may ban your account if detected.

- Never share your Discord token publicly
- Keep your token secure
- This is for educational purposes only
