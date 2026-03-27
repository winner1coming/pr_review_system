def is_valid_pr(pr):
    # 1️⃣ 必须有 review comment
    if pr.get("review_comments", 0) == 0:
        return False

    # 2️⃣ 过滤垃圾 PR
    title = pr["title"].lower()
    INVALID_KEYWORDS = ["typo", "doc", "readme", "chore", "bump"]

    if any(k in title for k in INVALID_KEYWORDS):
        return False

    # 3️⃣ 过滤 bot
    if "bot" in pr["user"]["login"].lower():
        return False

    return True