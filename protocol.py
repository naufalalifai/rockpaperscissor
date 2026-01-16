DELIMITER = "|"
ENCODING = "utf-8"

def encode_message(msg_type: str, payload: str = "") -> bytes:
    """
    Serialize message into bytes.
    Format: TYPE|payload
    """
    message = f"{msg_type}{DELIMITER}{payload}"
    return message.encode(ENCODING)


def decode_message(data: bytes):
    """
    Deserialize bytes into (type, payload)
    """
    try:
        text = data.decode(ENCODING)
        parts = text.split(DELIMITER, 1)
        msg_type = parts[0]
        payload = parts[1] if len(parts) > 1 else ""
        return msg_type, payload
    except Exception:
        return "ERROR", "Malformed message"
