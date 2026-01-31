from flask import Flask, render_template, request, send_file, after_this_request
import os
import io
from crypto import encrypt_data, decrypt_data
from stego import embed_data, extract_data

app = Flask(__name__)
# 50MB max upload
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        # Get inputs
        image_file = request.files.get('image')
        secret_file = request.files.get('secret_file')
        text_data = request.form.get('secret_text')
        password = request.form.get('password')

        if not image_file or not password:
            return "Missing image or password", 400

        if not secret_file and not text_data:
            return "No secret data provided", 400
            
        # Prepare secret bytes
        if secret_file:
            secret_bytes = secret_file.read()
            # If it's a file, we might want to store filename, but requirement 
            # says "never hardcoded". For simplicity in this purely browser-based tool,
            # we'll just handle raw content. If restoring a file is needed, 
            # we should prepend filename + null byte.
            # Let's support basic filename preservation properly.
            filename = os.path.basename(secret_file.filename).encode('utf-8')
            # Format: [FilenameLength(4)][Filename][Content]
            # Actually, simpler: JUST content. The user knows what they hid (educational).
            # But "User uploads a secret file OR enters plain text".
            # If text, we treat as bytes.
            pass  # secret_bytes is ready
        else:
            secret_bytes = text_data.encode('utf-8')

        # Encrypt
        encrypted_payload = encrypt_data(secret_bytes, password)
        
        # Embed
        output_image = embed_data(image_file, encrypted_payload)
        
        # Return as downloadable PNG
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='stego_image.png')

    except Exception as e:
        return str(e), 500

@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        image_file = request.files.get('image')
        password = request.form.get('password')

        if not image_file or not password:
            return "Missing image or password", 400

        # Extract
        try:
            encrypted_payload = extract_data(image_file)
        except ValueError as e:
            # If extraction fails (no data or corruption)
            return f"Extraction failed: {str(e)}", 400

        # Decrypt
        try:
            decrypted_data = decrypt_data(encrypted_payload, password)
        except ValueError as e:
            return f"Decryption failed: {str(e)}", 403

        # Return data
        # We need to decide if we download as file or show text.
        # Since we didn't strictly store mime type, we'll try to guess or just return binary.
        # If it looks like UTF-8 text, maybe return text?
        # Requirement: "return original file/text"
        
        # Heuristic: Try decode as utf-8. If valid, return as text/plain. Else application/octet-stream
        try:
            text_content = decrypted_data.decode('utf-8')
            # If it has specific control chars, might be binary.
            # But simple text usually works.
            # Let's wrap it in a response that the frontend can handle.
            # Or just send file.
            
            # Robust way: Send as a file download "secret.bin" or "secret.txt" 
            # and let user rename, OR send generic bytes.
            
            # Improvement: Let's assume binary download by default, 
            # but if it decodes cleanly to text, we can show that on frontend?
            # Backend just sends bytes.
            
            return send_file(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                download_name='secret_extracted.bin' if not text_content.isprintable() else 'secret.txt',
                mimetype='application/octet-stream'
            )
            
        except UnicodeDecodeError:
             return send_file(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                download_name='secret_extracted.bin',
                mimetype='application/octet-stream'
            )

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
