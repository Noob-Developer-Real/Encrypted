from cryptography.fernet import Fernet
from dotenv import load_dotenv
import requests
import os

load_dotenv()

def _get_fernet() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in your .env file.")
    return Fernet(key.encode())


def encrypt_file(data: bytes) -> bytes:
    return _get_fernet().encrypt(data)


def decrypt_file(data: bytes) -> bytes:
    return _get_fernet().decrypt(data)

def send_document(file):
    token   = os.getenv("token")
    chat_id = os.getenv("chat_id")

    raw_bytes       = file.read()
    encrypted_bytes = encrypt_file(raw_bytes)

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    response = requests.post(
        url,
        data={"chat_id": chat_id},
        files={"document": ("encrypted.bin", encrypted_bytes, "application/octet-stream")},
    )
    return response.json()


def get_file_url(file_id: str) -> str | None:
    """
    Given a Telegram file_id, returns a direct download URL
    to the encrypted file stored on Telegram.
    """
    token = os.getenv("token")
    if not token or not file_id:
        return None

    try:
        response = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": file_id},
            timeout=10,
        )
        data = response.json()

        if data.get("ok"):
            file_path = data["result"]["file_path"]
            return f"https://api.telegram.org/file/bot{token}/{file_path}"

    except Exception as e:
        print(f"get_file_url error: {e}")

    return None


def fetch_and_decrypt(file_id: str) -> bytes | None:
    """
    Full pipeline: file_id → download encrypted file → decrypt → raw bytes.
    Used by the image proxy view to serve images to the browser.
    """
    url = get_file_url(file_id)
    if not url:
        return None

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return decrypt_file(response.content)

    except Exception as e:
        print(f"fetch_and_decrypt error: {e}")
        return None


def delete_local_file(file_field):
    """Safely deletes a file from local storage."""
    if not file_field:
        return False
    try:
        file_path = file_field.path
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"File delete error: {e}")
    return False
