from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from pr_review_system.github_api.client import GitHubClient
from pr_review_system.github_api.pr_service import filter_files
from pr_review_system.prompt.architecture_review_prompt import build_architecture_review_system_prompt, build_architecture_review_user_prompt
from pr_review_system.prompt.code_style_review_prompt import build_style_review_system_prompt, build_style_review_user_prompt
from pr_review_system.prompt.correctness_review_prompt import build_correctness_review_system_prompt, build_correctness_review_user_prompt
from pr_review_system.prompt.tech_review_prompt import build_tech_review_system_prompt, build_tech_review_user_prompt
from pr_review_system.review.aggregator import aggregate_all
from pr_review_system.utils.diff_utils import extract_diff
from pr_review_system.prompt.builder import PromptBuilder
from pr_review_system.llm.client import LLMClient
from pr_review_system.output.writer import save_results
from pr_review_system.review.get_valid_prs import get_valid_prs
from pr_review_system.config import MAX_PRS
from pr_review_system.backgroup.get_backgroup import BackGround, format_architecture_summary, format_code_style_summary, format_dependency_summary, format_readme_summary
from pr_review_system.evaluation.evalution_base import EvalutionBase

import time


class Reviewer:

    def __init__(self):
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()
        self.background = BackGround()
    
    def safe_json_parse(self, text):
        try:
            text = text.strip().replace("```json", "").replace("```", "")
            return json.loads(text)
        except:
            return []
        
    def parse_summary_json(self, text):
        if not text or not isinstance(text, str):
            return {}

        try:
            text = text.strip().replace("```json", "").replace("```", "")
            data = json.loads(text)

            if isinstance(data, dict):
                return data
            else:
                print("⚠️ summary 解析结果不是 dict")
                return {}

        except Exception as e:
            print("❌ summary JSON 解析失败:", e)
            return {}

    def run_parallel_reviews(self, diff, commit_info, code_summary,readme_summary, architecture_summary, dependency_summary):

        with ThreadPoolExecutor(max_workers=4) as executor:

                futures = {
                    "style": executor.submit(
                        self.llm.review,
                        {
                            "system": build_style_review_system_prompt(),
                            "user": build_style_review_user_prompt(
                                code_summary,
                                diff,
                                commit_info
                            )
                        }
                    ),

                    "correctness": executor.submit(
                        self.llm.review,
                        {
                            "system": build_correctness_review_system_prompt(),
                            "user": build_correctness_review_user_prompt(
                                readme_summary,
                                diff,
                                commit_info
                            )
                        }
                    ),

                    "architecture": executor.submit(
                        self.llm.review,
                        {
                            "system": build_architecture_review_system_prompt(),
                            "user": build_architecture_review_user_prompt(
                                architecture_summary,
                                diff,
                                commit_info
                            )
                        }
                    ),

                    "tech": executor.submit(
                        self.llm.review,
                        {
                            "system": build_tech_review_system_prompt(),
                            "user": build_tech_review_user_prompt(
                                dependency_summary,
                                diff,
                                commit_info
                            )
                        }
                    )
                }

                results = []

                for key, future in futures.items():
                    try:
                        raw = future.result()
                        parsed = self.safe_json_parse(raw)
                        results.extend(parsed)
                    except Exception:
                        results.extend([])

        return results

    def run(self, repo_name):
        owner, repo = repo_name.split("/")
        time.sleep(0.5)
        prs = get_valid_prs(self.github ,owner, repo, MAX_PRS)
        background = self.background.get_background(owner, repo)
        code_summary = format_code_style_summary(self.parse_summary_json(background.get("code_summary", "")))
        readme_summary = format_readme_summary(self.parse_summary_json(background.get("readme_summary", "")))
        architecture_summary = format_architecture_summary(self.parse_summary_json(background.get("tree_summary", "")))
        dependency_summary = format_dependency_summary(self.parse_summary_json(background.get("dependency_summary", "")))

        results = []

        for pr_with_comments in prs:
            pr_number = pr_with_comments["pr"]["number"]
            review_comments = pr_with_comments["review_comments"]
            print(f"\n===== PR #{pr_number} =====")

            files = self.github.get_pr_files(owner, repo, pr_number)
            files = filter_files(files)
            
            diff = extract_diff(files)
            commits = self.github.get_pr_commits(owner, repo, pr_number)
            commit_info = [{"sha": c["sha"], "message": c["commit"]["message"]} for c in commits]


            startTime = time.time()
            #prompt = self.prompt_builder.build("with_readme", diff, commit_info, background)
            #review = self.llm.review(prompt)
            parallel_reviews = self.run_parallel_reviews(diff, commit_info, code_summary, readme_summary, architecture_summary, dependency_summary)
            metrics, score = aggregate_all(parallel_reviews)

            duration = round(time.time() - startTime, 2)

            results.append({
                "repo": repo_name,
                "pr": pr_number,
                "metrics": metrics,
                "score": score,
                "parallel_reviews": parallel_reviews,
                "commits": commit_info,
                "review_comments": review_comments,
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "duration": duration
            })
            time.sleep(1)
        evaluator = EvalutionBase()
        evaluator.evaluate(results)
        save_results(results)

        