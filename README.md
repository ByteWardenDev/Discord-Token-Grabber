# Discord Token Extractor

This script extracts Discord tokens from various browsers and Discord installations, then uploads them to a specified webhook. It is intended for educational purposes only.

## Features
- **Token Extraction**:
  - Supports Discord, Discord PTB, Canary, Lightcord, and several browsers.
  - Decrypts encrypted tokens using master keys.
- **Validation**: Ensures tokens are active by verifying them with Discord's API.
- **Webhook Integration**: Sends extracted tokens to a given webhook URL.
- **Modular Design**: Organized into classes for easy customization and reuse.

## Usage
1. Replace `webhook_url` with your Discord webhook URL.
2. Run the script to extract and send valid tokens.

**Warning**: Use responsibly and only on systems where you have explicit permission.
