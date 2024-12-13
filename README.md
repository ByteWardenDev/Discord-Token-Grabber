# Discord Token Grabber

This script extracts Discord tokens from different browsers and sends them to a specified Discord webhook URL. It is designed for educational purposes to demonstrate how web browsers store tokens and how one might retrieve them. **Please use this responsibly** and never use this script for malicious purposes.

## Features

- Extracts Discord tokens from popular browsers and Discord clients.
- Supports browsers: Chrome, Opera, Brave, Microsoft Edge, Yandex.
- Supports Discord clients: Discord, Discord Canary, Discord PTB.
- Decrypts encrypted tokens using the Windows Cryptography API (via AES decryption).
- Validates tokens by sending a request to Discord's API.
- Sends valid tokens to a specified Discord webhook.

## How It Works

1. **Extract Tokens:**
   The script scans local storage files from browsers and Discord clients for any stored authentication tokens.
   
2. **Decrypt Tokens:**
   Encrypted tokens are decrypted using the `AES` encryption algorithm.

3. **Validate Tokens:**
   Extracted tokens are validated by making a request to Discord's API to ensure they are valid.

4. **Send Tokens to Webhook:**
   Valid tokens are then sent to a configured Discord webhook URL via a POST request.

## Requirements

- Python 3.x
- Required libraries:
  - `requests`
  - `pycryptodome`
  - `win32crypt`
- Windows operating system (as the script uses Windows-specific APIs for token decryption)

## Setup

1. Clone the repository or download the script to your local machine.

2. Install the required dependencies using `pip`:

    ```bash
    pip install requests pycryptodome pypiwin32
    ```

3. Set your **Discord webhook URL**:

    - Open your Discord server settings, navigate to the *Webhooks* section, and create a new webhook.
    - Copy the webhook URL and replace `"WEBHOOK URL"` in the script with your copied URL.

4. Run the script:

    ```bash
    python Main.py
    ```

   The script will search for Discord tokens and send any valid ones to your specified webhook.
