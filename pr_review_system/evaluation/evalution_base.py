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

    def is_matched(self, people_review, llm_review):
        system = build_match_base_prompt()
        user = build_match_base_user_prompt(people_review, llm_review)
        prompt = {
            "system": system,
            "user": user
        }
        result = self.llm.review(prompt, temperature=0.0)

        try:
            result_json = json.loads(result)
            return result_json.get("match", 0) == 1
        except:
            print("解析结果失败:", result)
            return False
        
    def compute_recall(self, people_reviews, llm_reviews):
        if not people_reviews:
            return None
        
        matched = 0
        for review in people_reviews:
            if self.is_matched(review, llm_reviews):
                matched += 1
        
        recall = matched / len(people_reviews) if people_reviews else 0
        return recall

    def evaluate(self, results):
        eval_results= []
        for item in results:
            people_reviews = item["review_comments"]
            llm_review = item["review"]
            recall = self.compute_recall(people_reviews, llm_review)
            eval_results.append({
                "repo": item["repo"],
                "pr": item["pr"],
                "strategy": item["strategy"],
                "recall": recall,
                "time": item["time"]
            })

        save_eval_results(eval_results)