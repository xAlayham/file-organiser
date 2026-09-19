import hashing
import os
import scanner

def find_duplicates(folder: str) -> dict:
    """Matches files with identical content by hash and groups them"""
    hashes = {}
    files = scanner.scan_folder(folder)

    for filename in files:
        full_path = os.path.join(folder, filename)
        file_hash = hashing.get_file_hash(full_path)

        if file_hash not in hashes:
            hashes[file_hash] = []
        hashes[file_hash].append(filename)

    duplicates = {}
    for file_hash, filenames in hashes.items():
        if len(filenames) > 1:
            original = filenames[0]
            for duplicate in filenames[1:]:
                if original not in duplicates:
                    duplicates[original] = []
                duplicates[original].append(duplicate)
    return duplicates
