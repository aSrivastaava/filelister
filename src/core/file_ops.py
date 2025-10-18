import os
from datetime import datetime


def list_dir(path):
    """Return a sorted list of (name, full_path, is_dir, size, mtime) for immediate children of path."""
    items = []
    try:
        for name in sorted(os.listdir(path), key=lambda s: s.lower()):
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            try:
                size = os.path.getsize(full) if not is_dir else None
            except Exception:
                size = None
            try:
                mtime = os.path.getmtime(full)
            except Exception:
                mtime = None
            items.append((name, full, is_dir, size, mtime))
    except Exception:
        # return empty list on error
        return []
    return items


def format_size(size_bytes):
    if size_bytes is None:
        return ''
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            if unit == 'bytes':
                return f"{size_bytes:,} {unit}"
            else:
                return f"{size_bytes/1024.0:.2f} {unit}"
        size_bytes /= 1024.0


def format_mtime(mtime):
    if not mtime:
        return ''
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
