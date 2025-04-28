import os
import hashlib

def file_hash(filepath):
    """Return the MD5 hash of the file specified by filepath."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except IOError:
        print(f"Could not read file: {filepath}")
        return None
    return hash_md5.hexdigest()

def find_duplicates(directory):
    """Find and print duplicate files in the given directory."""
    hashes = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filehash = file_hash(filepath)
            if filehash:
                if filehash in hashes:
                    duplicates.append((filepath, hashes[filehash]))
                else:
                    hashes[filehash] = filepath

    if duplicates:
        print("Duplicate files found:")
        for dup in duplicates:
            print(f"Duplicate: {dup[0]}")
            print(f"Original: {dup[1]}")
            print("-" * 40)
    else:
        print("No duplicate files found.")

# Example usage:
find_duplicates("../pythongames")