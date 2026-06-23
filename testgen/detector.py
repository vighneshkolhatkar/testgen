import os


SUPPORTED = {".py": "python", ".java": "java"}


def detect_language(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext not in SUPPORTED:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED.keys())}"
        )
    return SUPPORTED[ext]
