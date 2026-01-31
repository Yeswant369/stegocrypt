import os
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Configuration
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # 256 bits
ITERATIONS = 600000

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 256-bit key from the password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypts data using AES-256-GCM.
    Format: [Salt(16)][Nonce(12)][DataLength(4)][Ciphertext]
    """
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    key = derive_key(password, salt)
    
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    # Pack everything: Salt + Nonce + Data Length + Ciphertext
    # We include original data length just in case, though usually optional for GCM
    # Actually, simplistic approach: Salt + Nonce + Ciphertext
    # The user requirements didn't specify exact binary format, but self-contained is best.
    
    return salt + nonce + ciphertext

def decrypt_data(payload: bytes, password: str) -> bytes:
    """
    Decrypts data using AES-256-GCM.
    Expects format: [Salt(16)][Nonce(12)][Ciphertext]
    """
    try:
        if len(payload) < SALT_SIZE + NONCE_SIZE:
            raise ValueError("Invalid payload size")

        salt = payload[:SALT_SIZE]
        nonce = payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        ciphertext = payload[SALT_SIZE + NONCE_SIZE:]
        
        key = derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext
    except Exception as e:
        # Generic error to avoid leaking details, though exceptions are caught by caller
        raise ValueError("Decryption failed: Incorrect password or corrupted data") from e
