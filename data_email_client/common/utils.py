from cryptography.fernet import Fernet
from data_email_client.common.models import EmailSettings
import getpass
import json
import os
from pathlib import Path


USERNAME = getpass.getuser()
HOME_DIR = Path(os.path.expanduser("~/"))
PACKAGE_DIR = HOME_DIR / ".data_email_client"
PACKAGE_DIR.mkdir(exist_ok=True)
KEY_FILE = PACKAGE_DIR / "key.key"
CONFIG_FILE = PACKAGE_DIR / ".data_mail_client.conf"


def generate_key() -> bytes:
    """Generate a key for encryption and decryption"""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key


def load_key() -> bytes:
    """Load the key from the key file"""
    return open(KEY_FILE, "rb").read()


def encrypt_password(password: str, key: bytes) -> str:
    """Encrypt the password"""
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Decrypt the password"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()


def load_settings_if_exists() -> dict:
    settings_file = (
        "path_to_settings_file"  # Replace with the actual path to your settings file
    )
    if os.path.exists(settings_file):
        load_settings()


def load_settings() -> EmailSettings:
    if not os.path.exists(CONFIG_FILE):
        return EmailSettings()

    with open(CONFIG_FILE, "r") as file:
        email_settings = EmailSettings(**json.load(file))
        email_settings.password = retrieve_password(email_settings.password)
    return email_settings


def store_settings(email_settings: EmailSettings, store_password: bool) -> None:
    if store_password:
        if not os.path.exists(CONFIG_FILE):
            key = generate_key()
        else:
            key = load_key()
        encrypted_password = encrypt_password(email_settings.password, key)
        email_settings.password = encrypted_password

    with open(CONFIG_FILE, "w") as file:
        file.write(email_settings.model_dump_json())


def retrieve_password(encrypted_password: str) -> str:
    if encrypted_password:
        key = load_key()
        return decrypt_password(encrypted_password, key)
    return None
