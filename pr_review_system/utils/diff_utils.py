def extract_diff(files):
    diffs = []
    for f in files:
        if "patch" in f:
            diffs.append(f"文件: {f['filename']}\n{f['patch']}")
    return "\n\n".join(diffs)