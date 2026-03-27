def is_valid_pr(pr):
    # 2️⃣ 标题过滤（轻量，不要过度）
    title = pr.get("title", "").lower()

    INVALID_KEYWORDS = ["typo", "chore", "bump", "format"]

    if any(k in title for k in INVALID_KEYWORDS):
        return False

    # 3️⃣ 过滤 bot
    user = pr.get("user", {}).get("login", "").lower()
    if "bot" in user:
        return False

    return True