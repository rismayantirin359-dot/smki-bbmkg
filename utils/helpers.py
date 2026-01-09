import base64, io

def decode_signature(base64_data):
    try:
        _, encoded = base64_data.split(",", 1)
        return io.BytesIO(base64.b64decode(encoded))
    except Exception:
        return None

def safe_filename(nama):
    return "".join(
        c for c in nama if c.isalnum() or c in (" ", "_", "-")
    ).strip().replace(" ", "_")
