import os
import time
import random
import requests
from datetime import datetime
from groq import Groq

# Configuration - Set these as environment variables or modify here
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") or ""
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID_STR = os.getenv("CHANNEL_ID", "")
CHANNEL_ID = CHANNEL_ID_STR if CHANNEL_ID_STR else ""

# Message settings
MIN_MESSAGE_INTERVAL = 60  # Minimum seconds between messages (to avoid rate limits)
MAX_MESSAGE_INTERVAL = 300  # Maximum seconds between messages

# Game context for more relevant messages
GAME_CONTEXT = """
You're a casual Roblox player in "Rebirth Champions Ultimate" Discord. Type like texting a friend - casual, relaxed, sometimes lazy grammar.

About you:
- Hatched 10-13 million ornament eggs across all accounts
- Run 7 alts for hatching
- Got some secrets, decent rebirths, skill tree maxed
- Christmas ornament egg is fire, event is OP
- Bought gamepasses for alts during 50% sale

Game topics: hatching eggs, rebirths, secrets, skill tree, Christmas event, ornament eggs, gamepasses, alts, grinding, pulls, champions.

CRITICAL RULES:
- Only use words that make sense in context
- If responding to chat, react to what they're ACTUALLY saying about the game
- If chat is quiet, mention something game-related (eggs, rebirths, event, etc.)
- Keep messages SHORT (20-60 chars)
- Use casual slang: "rn", "fr", "ngl", "tbh", "lol", "yeah", "nah"
- Don't use random words that don't fit - keep it game-related
- Make sure your message actually makes sense
"""

MESSAGE_PROMPTS = [
    "Write a super casual Discord message about hatching eggs rn, like you're just chatting",
    "Type a quick casual message about the Christmas event, like talking to friends",
    "Write a short casual message asking about the game or reacting to something",
    "Type a quick message about rebirths or your progress, super casual",
    "Write a brief casual message about your alts, like you're just mentioning it",
    "Type a quick reaction to the giveaway or sale, super casual",
    "Write a short casual message about something that just happened in game",
    "Type a quick question about the game, super casual like asking a friend",
    "Write a brief message about what you're doing rn, super casual",
    "Type a quick casual comment, like you're just hanging out in chat",
    "Write a short casual reaction to something, super relaxed",
    "Type a quick casual message, like you're just checking in casually",
]

class DiscordAutoLevel:
    def __init__(self):
        self.groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.recent_messages = []  # Track recent messages to avoid repetition
        self.max_recent_history = 10  # Keep last 10 messages to avoid repeats
        self.last_prompt_type = None  # Track last prompt type to vary
        
    def generate_message(self):
        """Generate a message using Groq API - NO FALLBACKS, only Groq
        Returns tuple: (message_text, reply_to_message_id)"""
        if not self.groq_client:
            print("ERROR: GROQ_API_KEY not set! Cannot generate messages.")
            return None, None
        
        # Get recent chat messages for context
        recent_data = self.get_recent_messages(limit=8)
        recent_chat = recent_data.get('context', [])
        message_list = recent_data.get('messages', [])
        
        # Retry logic for API calls
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Build conversation history to avoid repetition
                messages = [{"role": "system", "content": GAME_CONTEXT}]
                
                # Add recent chat context if available
                if recent_chat and len(recent_chat) > 0:
                    chat_text = "\n".join(recent_chat[-5:])  # Last 5 messages
                    messages.append({
                        "role": "user",
                        "content": f"Recent chat messages:\n{chat_text}\n\nRespond naturally to what people are saying. React to their messages casually. If you mention someone by name, you're replying to them. Don't ask what they're talking about - just respond to it. Don't make up numbers - only mention things that make sense based on the conversation."
                    })
                else:
                    # No recent chat, send a casual game-related message
                    casual_topics = [
                        "Drop a super casual message about hatching eggs or playing the game",
                        "Write a quick casual message about the Christmas event or your progress",
                        "Type a brief casual comment about rebirths or the game, super relaxed",
                        "Write a short casual message about what you're doing in game rn",
                    ]
                    topic = random.choice(casual_topics)
                    messages.append({
                        "role": "user",
                        "content": f"Chat is quiet. {topic}. Keep it super casual and short. Don't ask questions - just make a casual comment."
                    })
                
                # Add our recent messages to avoid repetition
                if self.recent_messages:
                    recent = ', '.join(self.recent_messages[-3:])
                    messages.append({
                        "role": "user", 
                        "content": f"Don't repeat these messages you just sent: {recent}. Write something different."
                    })
                
                # Vary temperature for more diversity (0.9 to 1.0 for more natural responses)
                temperature = random.uniform(0.9, 1.0)
                
                # Use available models (removed decommissioned mixtral)
                models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
                model = random.choice(models)
                
                completion = self.groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=random.randint(60, 100),  # Vary token length
                    temperature=temperature,
                )
                message = completion.choices[0].message.content.strip()
                
                # Remove quotes if Groq adds them
                if message.startswith('"') and message.endswith('"'):
                    message = message[1:-1]
                if message.startswith("'") and message.endswith("'"):
                    message = message[1:-1]
                
                # Check if message is too similar to recent messages
                message_lower = message.lower()
                is_similar = any(
                    self._similarity(message_lower, recent.lower()) > 0.7 
                    for recent in self.recent_messages
                )
                
                if is_similar and len(self.recent_messages) > 0:
                    print(f"Message too similar to recent, regenerating...")
                    continue  # Retry with different prompt
                
                # Ensure message isn't too long
                if len(message) > 200:
                    message = message[:197] + "..."
                
                # Ensure message isn't empty
                if not message or len(message.strip()) == 0:
                    continue
                
                # Add to recent messages history
                self.recent_messages.append(message)
                if len(self.recent_messages) > self.max_recent_history:
                    self.recent_messages.pop(0)
                
                # Check if message mentions a username and find their message to reply to
                reply_to_id = None
                if message_list:
                    message_lower = message.lower()
                    # Check if message contains any username from recent messages
                    for msg_data in message_list[-5:]:  # Check last 5 messages
                        username = msg_data['username'].lower()
                        # Check if message mentions the username (as a word, not substring)
                        if username in message_lower:
                            # Find the word boundary to avoid partial matches
                            import re
                            pattern = r'\b' + re.escape(username) + r'\b'
                            if re.search(pattern, message_lower):
                                reply_to_id = msg_data['message_id']
                                print(f"Detected mention of {msg_data['username']}, will reply to their message")
                                break
                    
                return message, reply_to_id
            except Exception as e:
                print(f"Error generating message (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    print("Failed to generate message after retries. Skipping this cycle.")
                    return None, None
        
        return None, None
    
    def get_recent_messages(self, limit=10):
        """Get recent messages from the Discord channel"""
        url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages?limit={limit}"
        
        headers = {
            "Authorization": DISCORD_TOKEN,
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                # Filter out our own messages and format for context
                chat_context = []
                message_data = []  # Store full message data for replies
                for msg in messages:
                    # Skip our own messages (check if author ID matches current user)
                    author_id = msg.get('author', {}).get('id', '')
                    # Skip if it's our own message (you can add your user ID check here if needed)
                    # if author_id == 'YOUR_USER_ID':
                    #     continue
                    content = msg.get('content', '').strip()
                    if content and len(content) > 0:
                        username = msg.get('author', {}).get('username', 'someone')
                        chat_context.append(f"{username}: {content}")
                        message_data.append({
                            'username': username,
                            'message_id': msg.get('id'),
                            'content': content
                        })
                
                # Return both formatted context and message data
                return {
                    'context': chat_context[::-1],  # Reverse to show oldest first
                    'messages': message_data[::-1]  # Reverse to match context order
                }
            else:
                print(f"Failed to get messages. Status: {response.status_code}")
                return {'context': [], 'messages': []}
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return {'context': [], 'messages': []}
    
    def _similarity(self, msg1, msg2):
        """Simple similarity check between two messages"""
        # Check word overlap
        words1 = set(msg1.split())
        words2 = set(msg2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def send_message(self, message, reply_to_message_id=None):
        """Send a message to Discord using REST API
        If reply_to_message_id is provided, replies to that message"""
        url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
        
        headers = {
            "Authorization": DISCORD_TOKEN,
            "Content-Type": "application/json",
        }
        
        data = {
            "content": message
        }
        
        # Add message reference if replying
        if reply_to_message_id:
            data["message_reference"] = {
                "message_id": reply_to_message_id
            }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent: {message}")
                return True
            else:
                print(f"Failed to send message. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_user_info(self):
        """Get user info to verify token works"""
        url = "https://discord.com/api/v9/users/@me"
        headers = {
            "Authorization": DISCORD_TOKEN,
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"Logged in as: {user_data.get('username', 'Unknown')}#{user_data.get('discriminator', '0000')}")
                print(f"User ID: {user_data.get('id', 'Unknown')}")
                return True
            else:
                print(f"Failed to get user info. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error getting user info: {e}")
            return False
    
    def run(self):
        """Main loop that sends messages at random intervals"""
        if not DISCORD_TOKEN:
            print("ERROR: DISCORD_TOKEN not set!")
            print("Please set it as an environment variable or in the script.")
            return
        
        if not CHANNEL_ID:
            print("ERROR: CHANNEL_ID not set!")
            print("Please set it as an environment variable or in the script.")
            return
        
        if not GROQ_API_KEY:
            print("ERROR: GROQ_API_KEY not set!")
            print("Please set it as an environment variable.")
            return
        
        # Verify token works
        print("Verifying Discord token...")
        if not self.get_user_info():
            print("ERROR: Invalid Discord token or unable to connect!")
            return
        
        print(f"Starting message loop for channel: {CHANNEL_ID}")
        print("Press Ctrl+C to stop.")
        
        # Main loop
        while True:
            try:
                message, reply_to_id = self.generate_message()
                if message:
                    self.send_message(message, reply_to_id)
                else:
                    print("No message generated, skipping send.")
                
                # Wait for a random interval before next message
                wait_time = random.randint(MIN_MESSAGE_INTERVAL, MAX_MESSAGE_INTERVAL)
                print(f"Waiting {wait_time} seconds before next message...")
                time.sleep(wait_time)
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Unexpected error in main loop: {e}")
                time.sleep(10)  # Wait a bit before retrying

if __name__ == "__main__":
    bot = DiscordAutoLevel()
    bot.run()
