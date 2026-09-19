import hashlib

CHUNK_SIZE = 65536

def get_file_hash(path: str) -> str:
    """Return the SHA-256 hash of a file's contents, reading it in chunks."""
    digest = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)

    return digest.hexdigest()
