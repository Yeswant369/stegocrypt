import io
import os
from crypto import encrypt_data, decrypt_data
from stego import embed_data, extract_data
from PIL import Image

def test_steganography_flow():
    print("Starting verification...")
    
    # 1. Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    print("1. Created dummy image.")

    # 2. Define secret data and password
    secret_text = "This is a super secret message verification."
    password = "MyStrongPassword123!"
    secret_bytes = secret_text.encode('utf-8')
    print(f"2. Secret data: '{secret_text}'")

    # 3. Encrypt data
    encrypted_payload = encrypt_data(secret_bytes, password)
    print(f"3. Encrypted data length: {len(encrypted_payload)} bytes")

    # 4. Embed data
    # We pass the bytesIO of the image
    stego_image = embed_data(img_byte_arr, encrypted_payload)
    print("4. Data embedded into image.")

    # 5. Save stego image to bytes (simulating download)
    stego_byte_arr = io.BytesIO()
    stego_image.save(stego_byte_arr, format='PNG')
    stego_byte_arr.seek(0)
    print("5. Stego image saved (simulating download).")

    # 6. Extract data
    extracted_payload = extract_data(stego_byte_arr)
    print(f"6. Extracted payload length: {len(extracted_payload)} bytes")
    
    # Check if payloads match
    if extracted_payload != encrypted_payload:
        print("ERROR: Extracted payload does not match encrypted payload!")
        return

    # 7. Decrypt data
    try:
        decrypted_bytes = decrypt_data(extracted_payload, password)
        decrypted_text = decrypted_bytes.decode('utf-8')
        print(f"7. Decrypted text: '{decrypted_text}'")
        
        if decrypted_text == secret_text:
            print("\nSUCCESS: Verification Passed! End-to-end flow works.")
        else:
            print("\nFAILURE: Decrypted text does not match original.")
            
    except Exception as e:
        print(f"\nFAILURE: Decryption threw exception: {e}")

if __name__ == "__main__":
    test_steganography_flow()
