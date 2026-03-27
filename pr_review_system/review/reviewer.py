import json

from pr_review_system.github_api.client import GitHubClient
from pr_review_system.github_api.pr_service import filter_files
from pr_review_system.utils.diff_utils import extract_diff
from pr_review_system.prompt.builder import PromptBuilder
from pr_review_system.llm.client import LLMClient
from pr_review_system.output.writer import save_results
from pr_review_system.evaluation.evalution_base import EvalutionBase
from pr_review_system.review.get_valid_prs import get_valid_prs
from pr_review_system.config import MAX_PRS

import time

class Reviewer:

    def __init__(self):
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

    def run(self, repo_name):
        owner, repo = repo_name.split("/")

        prs = get_valid_prs(self.github,owner, repo, MAX_PRS)
        readme = self.github.get_readme(owner, repo)

        results = []

        for pr in prs:
            pr_number = pr["number"]
            print(f"\n===== PR #{pr_number} =====")

            files = self.github.get_pr_files(owner, repo, pr_number)
            files = filter_files(files)

            if not files:
                print("跳过（无有效代码）")
                continue

            diff = extract_diff(files)
            commits = self.github.get_pr_commits(owner, repo, pr_number)
            commit_info = [{"sha": c["sha"], "message": c["commit"]["message"]} for c in commits[-3:]]
            comments = self.github.get_review_comments(owner, repo, pr_number)
            people_reviews = self.github.get_reviews(owner, repo, pr_number)
            issue_comments = self.github.get_issue_comments(owner, repo, pr_number)
            review_comments = []
            review_comments += [c["body"] for c in comments if c["body"]]
            review_comments += [r["body"] for r in people_reviews if r["body"]]
            review_comments += [c["body"] for c in issue_comments if c["body"]]

            print(f"评论{review_comments}")

            if not review_comments:
                print("跳过（无评论）")
                continue

            for strategy in ["baseline", "with_readme"]:
                startTime = time.time()
                prompt = self.prompt_builder.build(strategy, diff, commit_info, readme)
                review = self.llm.review(prompt)
                parsed_review = json.loads(review)
                results.append({
                    "repo": repo_name,
                    "pr": pr_number,
                    "strategy": strategy,
                    "review": parsed_review,
                    "commits": commit_info,
                    "review_comments": review_comments,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })
                endTime = time.time()
                print(f"👉 策略:{strategy},耗时: {endTime - startTime:.2f} 秒")
                time.sleep(1)
            evaluator = EvalutionBase()
            evaluator.evaluate(results)
            save_results(results)

        