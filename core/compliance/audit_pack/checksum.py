import hashlib


def compute_checksum(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
