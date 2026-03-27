from pr_review_system.config import SUPPORTED_EXTENSIONS

def filter_files(files):
    return [
        f for f in files
        if any(f["filename"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
    ]