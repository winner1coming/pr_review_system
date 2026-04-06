from pr_review_system.github_api.client import GitHubClient
from pr_review_system.output.writer import save_eval_results
from pr_review_system.prompt.builder import PromptBuilder
from pr_review_system.llm.client import LLMClient
from pr_review_system.prompt.system_prompt import build_match_base_prompt
from pr_review_system.prompt.user_prompt import build_match_base_user_prompt
import json


class EvalutionBase:
    def __init__(self):
        self.llm = LLMClient()
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()

    def normalize_llm_review(self,llm_review_json):
        try:
            reviews = json.loads(llm_review_json)
        except:
            return llm_review_json  # fallback

        texts = []
        
        for i, r in enumerate(reviews):
            if r.get("confidence", 0) < 0.4:
                continue
            type = r.get("type", "")
            desc = r.get("description", "")
            advice = r.get("advice", "")
            conclution = r.get("conclusion", "")

            text = f"{i+1}.概括：{conclution} 问题类型：{type} 问题描述：{desc} 建议：{advice}"
            texts.append(text)

        return "\n".join(texts)
    
    def compute_match_score(self, people_review, llm_review):
        if not people_review or not llm_review:
            return None
        
        people_text = "\n".join([
            f"{i+1}. {r}" for i, r in enumerate(people_review)
        ])

        llm_text = self.normalize_llm_review(llm_review)
        
        system = build_match_base_prompt()
        user = build_match_base_user_prompt(people_text, llm_text)
        prompt = {
            "system": system,
            "user": user
        }
        result = self.llm.review(prompt, temperature=0.0)

        return result
        

    def evaluate(self, results, threshold=0.6):
        eval_results= []

        for item in results:
            people_review = item["review_comments"]
            llm_review = item["parallel_reviews"]

            score_result = self.compute_match_score(people_review, llm_review)
            result_json = {}
            try:
                result_json = json.loads(score_result)
            except:
                print("评分解析失败，返回原始结果作为分数：", score_result)
            score = 0.0
            score = result_json.get("score", 0)
            #confidence = item.get("review").get("confidence", 1)  # 默认置信度为0.5
            #final_score = score *(0.5 + 0.5 * confidence)  # 根据置信度调整分数
            
            eval_results.append({
                "repo": item["repo"],
                "pr": item["pr"],
                "score": score,  
                "reason": result_json.get("reason", ""),
                "covered_aspects": result_json.get("covered_aspects", []),
                "missing_aspects": result_json.get("missing_aspects", []),
                "time": item["time"]
            })
        
        summary = []
        
        scores = [item["score"] for item in eval_results if item["score"] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        ratio = sum(1 for s in scores if s >= threshold) / len(scores)

        summary.append({
            "repo": results[0]["repo"] if results else "",
            "avg_score": round(avg_score, 4),
            "high_quality_ratio": round(ratio, 4),
            "num_samples": len(scores)
        })
        save_eval_results(eval_results, filename_front="detailed_eval_results")
        save_eval_results(summary, filename_front="summary_eval_results")