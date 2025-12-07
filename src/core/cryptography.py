from cryptography.fernet import Fernet
from src.core.config import FERNET_KEY
from src.core.logger import logger

cipher = Fernet(FERNET_KEY)

def encrypt_entity(key: str) -> str:
    logger.info(f"Encrypting entity with key")
    return cipher.encrypt(key.encode()).decode()

def decrypt_entity(enc_key: str) -> str:
    logger.info(f"Decrypting entity with encrypted key")
    return cipher.decrypt(enc_key.encode()).decode()
