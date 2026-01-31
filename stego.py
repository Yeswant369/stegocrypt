from PIL import Image
import struct

def embed_data(image_buffer, data: bytes) -> Image.Image:
    """
    Embeds binary data into an image using LSB steganography.
    Input: image_buffer (file-like object), data (bytes)
    Output: PIL Image object
    """
    img = Image.open(image_buffer).convert('RGB')
    
    # Prepend data length (4 bytes unsigned int)
    length_prefix = struct.pack('!I', len(data))
    payload = length_prefix + data
    
    # Check capacity
    width, height = img.size
    max_bytes = (width * height * 3) // 8
    if len(payload) > max_bytes:
        raise ValueError(f"Data too large for this image. Capacity: {max_bytes} bytes, Data: {len(payload)} bytes")
    
    # Convert payload to bit generator
    payload_bits = ''.join(f'{byte:08b}' for byte in payload)
    payload_iter = iter(payload_bits)
    
    pixels = img.load()
    
    try:
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Modify Red
                bit = next(payload_iter, None)
                if bit is not None:
                    r = (r & ~1) | int(bit)
                
                # Modify Green
                bit = next(payload_iter, None)
                if bit is not None:
                    g = (g & ~1) | int(bit)
                    
                # Modify Blue
                bit = next(payload_iter, None)
                if bit is not None:
                    b = (b & ~1) | int(bit)
                
                pixels[x, y] = (r, g, b)
                
                if bit is None:
                    return img
    except StopIteration:
        pass
        
    return img

def extract_data(image_buffer) -> bytes:
    """
    Extracts binary data from an LSB-encoded image.
    Input: image_buffer (file-like object)
    Output: extracted data (bytes)
    """
    img = Image.open(image_buffer).convert('RGB')
    width, height = img.size
    pixels = img.load()
    
    # Generator to yield LSBs
    def bit_generator():
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                yield r & 1
                yield g & 1
                yield b & 1

    bits = bit_generator()
    
    # Read first 32 bits (4 bytes) for length
    length_bits = ""
    for _ in range(32):
        try:
            length_bits += str(next(bits))
        except StopIteration:
            raise ValueError("Image does not contain valid steganographic data (too small)")
            
    try:
        data_len = struct.unpack('!I', int(length_bits, 2).to_bytes(4, byteorder='big'))[0]
    except Exception:
        raise ValueError("Failed to decode data length. Image might not contain hidden data.")
    
    # Sanity check on length
    max_bytes = (width * height * 3) // 8
    if data_len > max_bytes or data_len < 0:
        raise ValueError(f"Invalid data length detected: {data_len}. content may be corrupted or not present.")

    # Read the data bits
    data_bits = []
    total_bits = data_len * 8
    
    try:
        for _ in range(total_bits):
            data_bits.append(str(next(bits)))
    except StopIteration:
         raise ValueError("Unexpected end of image data while reading payload.")
         
    # Convert bits back to bytes
    bit_string = ''.join(data_bits)
    data = int(bit_string, 2).to_bytes(data_len, byteorder='big')
    
    return data
