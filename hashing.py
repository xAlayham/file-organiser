import hashlib

def get_file_hash(path: str) -> str:
    """Return the SHA-256 hash of a file's contents."""
    with open(path, "rb") as f:
        data = f.read()

    return hashlib.sha256(data).hexdigest()
