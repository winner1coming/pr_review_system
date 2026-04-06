import re
from difflib import SequenceMatcher

import json
from pr_review_system.llm.client import LLMClient

from pr_review_system.prompt.aggregator_prompt import build_aggregate_review_system_prompt, build_aggregate_review_user_prompt, build_aggregate_review_user_prompt

class Review:
    def __init__(self, data):
        self.type = data.get("type", "")
        self.conclusion = data.get("conclusion", "")
        self.description = data.get("description", "")
        self.evidence = data.get("evidence", "")
        self.advice = data.get("advice", "")
        self.confidence = float(data.get("confidence", 0))
        self.relevance = float(data.get("relevance", 0))
        self.severity = data.get("severity", "Low")
        self.llm = LLMClient()

    def to_dict(self):
        return self.__dict__


# ----------------------
# 1. 标准化
# ----------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_review(r):
    new_r = Review(r.to_dict())
    new_r.description = normalize_text(new_r.description)
    new_r.evidence = normalize_text(new_r.evidence)
    return new_r


# ----------------------
# 2. 相似度判断
# ----------------------
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate(r1, r2, threshold=0.8):
    return similarity(r1.description, r2.description) > threshold


# ----------------------
# 3. 合并策略
# ----------------------
def max_severity(s1, s2):
    order = {"Low": 1, "Medium": 2, "High": 3}
    return s1 if order.get(s1, 1) >= order.get(s2, 1) else s2


def merge_reviews(r1, r2):
    return Review({
        "type": r1.type,
        "conclusion": r1.conclusion,
        "description": r1.description,
        "evidence": r1.evidence,
        "advice": r1.advice,
        "confidence": max(r1.confidence, r2.confidence),
        "relevance": max(r1.relevance, r2.relevance),
        "severity": max_severity(r1.severity, r2.severity)
    })


# ----------------------
# 4. 去重
# ----------------------
def deduplicate_reviews(reviews):
    unique = []

    for r in reviews:
        found = False
        for i, u in enumerate(unique):
            if is_duplicate(r, u):
                unique[i] = merge_reviews(u, r)
                found = True
                break
        if not found:
            unique.append(r)

    return unique


# ----------------------
# 5. 指标计算
# ----------------------
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
    high_conf_bug_rate = len(high_conf_bug) / total if total else 0
    high_conf_rate = len(high_conf) / total if total else 0
    avg_conf = sum(get_conf(r) for r in reviews) / total if total else 0
    avg_rel = sum(get_rel(r) for r in reviews) / total if total else 0

    return {
        "total_reviews": total,
        "high_conf_reviews": len(high_conf),
        "high_conf_bugs": len(high_conf_bug),
        "high_conf_bug_rate": round(high_conf_bug_rate, 3),
        "high_conf_rate": round(high_conf_rate, 3),
        "avg_confidence": round(avg_conf, 3),
        "avg_relevance": round(avg_rel, 3)
    }


# ----------------------
# 6. 最终评分
# ----------------------
def compute_final_score(metrics):
    return round(
        0.4 * metrics["high_conf_bug_rate"] +
        0.3 * metrics["high_conf_rate"] +
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