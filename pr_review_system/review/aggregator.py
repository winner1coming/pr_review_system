def compute_metrics(reviews):
    total = len(reviews)

    def get_conf(r):
        try:
            return float(r.get("confidence", 0))
        except:
            return 0

    def get_rel(r):
            try:
                return float(r.get("relevance", 0))
            except:
                return 0

    high_conf = [r for r in reviews if get_conf(r) >= 0.8]
    high_conf_bug = [
            r for r in reviews
            if r.get("type") == "Bug" and get_conf(r) >= 0.8
        ]

    avg_conf = sum(get_conf(r) for r in reviews) / total if total else 0
    avg_rel = sum(get_rel(r) for r in reviews) / total if total else 0

    return {
        "total_reviews": total,
        "high_conf_reviews": len(high_conf),
        "high_conf_bugs": len(high_conf_bug),
        "avg_confidence": round(avg_conf, 3),
        "avg_relevance": round(avg_rel, 3)
    }


# ----------------------
# 6. 最终评分
# ----------------------
def compute_final_score(metrics):
    return round(
        0.4 * metrics["high_conf_bugs"] +
        0.3 * metrics["high_conf_reviews"] +
        0.2 * metrics["avg_relevance"] +
        0.1 * metrics["avg_confidence"],
        3
    )


# ----------------------
# 7. 主聚合函数
# ----------------------
'''def aggregate_all(reviewer_outputs):
    all_reviews = []

    for output in reviewer_outputs:
        for r in output:
            all_reviews.append(normalize_review(Review(r)))

    deduped = deduplicate_reviews(all_reviews)

    metrics = compute_metrics(deduped)
    score = compute_final_score(metrics)

    return deduped, metrics, score'''

def aggregate_all(reviews):
    '''prompt_system = build_aggregate_review_system_prompt()
    prompt_user = build_aggregate_review_user_prompt(reviews)
    prompt = {
        "system": prompt_system,
        "user": prompt_user
    }

    results = LLMClient().review(prompt, temperature=0.0)
    result_json = []
    # 解析结果
    try:
        result_json = json.loads(results)
    except Exception as e:
        print("解析聚合结果失败，返回空列表: ", e)'''

    metrics = compute_metrics(reviews)
    score = compute_final_score(metrics)

    return metrics, score