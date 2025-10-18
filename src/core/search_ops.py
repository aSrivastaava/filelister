import os


def find_in_file(path, term):
    """Search for term in a file; return True if found. Binary-safe attempt.
    Keep minimal for now.
    """
    try:
        with open(path, 'rb') as f:
            data = f.read()
            return term.encode('utf-8') in data
    except Exception:
        return False
