from typing import Any

def default_serializer(msg: Any) -> bytes:
    return str(msg).encode("utf-8")


def pydantic_json_serializer(msg: Any) -> bytes:
    if hasattr(msg, 'json'):
        return msg.json().encode('utf-8')
    elif isinstance(msg, dict):
        import json
        return json.dumps(msg).encode('utf-8')
    elif isinstance(msg, str):
        return msg.encode('utf-8')
    else:
        raise TypeError("Cannot serialize message for Kafka: unsupported type")