# ⚠️ SECURITY WARNING

**Your Discord token has been exposed!**

The token you shared has been added to the script. For security:

1. **REGENERATE YOUR TOKEN IMMEDIATELY** after testing:
   - Go to https://discord.com/developers/applications
   - Select your application
   - Go to "Bot" section
   - Click "Reset Token"
   - Copy the new token
   - Update it in the script or use environment variables

2. **Use Environment Variables Instead** (Recommended):
   ```powershell
   $env:DISCORD_TOKEN="your_new_token_here"
   $env:GROQ_API_KEY="your_groq_key"
   ```
   Then remove the hardcoded token from the script.

3. **Never share your token publicly** - anyone with your token can control your bot/account!

The current setup will work for testing, but please regenerate your token for security.

