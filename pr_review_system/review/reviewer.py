import json

from pr_review_system.github_api.client import GitHubClient
from pr_review_system.github_api.pr_service import filter_files
from pr_review_system.utils.diff_utils import extract_diff
from pr_review_system.prompt.builder import PromptBuilder
from pr_review_system.llm.client import LLMClient
from pr_review_system.output.writer import save_results
from pr_review_system.review.get_valid_prs import get_valid_prs
from pr_review_system.config import MAX_PRS
from pr_review_system.backgroup.get_backgroup import BackGround
from pr_review_system.evaluation.evalution_base import EvalutionBase

import time


class Reviewer:

    def __init__(self):
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()
        self.background = BackGround()

    def run(self, repo_name):
        owner, repo = repo_name.split("/")
        time.sleep(0.5)
        prs = get_valid_prs(self.github ,owner, repo, MAX_PRS)
        #readme = self.github.get_readme(owner, repo)
        background = self.background.get_background(owner, repo)

        results = []

        for pr_with_comments in prs:
            pr_number = pr_with_comments["pr"]["number"]
            review_comments = pr_with_comments["review_comments"]
            print(f"\n===== PR #{pr_number} =====")

            files = self.github.get_pr_files(owner, repo, pr_number)
            files = filter_files(files)
            
            diff = extract_diff(files)
            commits = self.github.get_pr_commits(owner, repo, pr_number)
            commit_info = [{"sha": c["sha"], "message": c["commit"]["message"]} for c in commits[-5:]]


            startTime = time.time()
            prompt = self.prompt_builder.build("with_readme", diff, commit_info, background)
            review = self.llm.review(prompt)
            results.append({
                "repo": repo_name,
                "pr": pr_number,
                "strategy": "with_readme",
                "review": review,
                "commits": commit_info,
                "review_comments": review_comments,
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            })
            print(f"commit:\n{commit_info}")
            endTime = time.time()
            print(f"👉 策略:with_readme,耗时: {endTime - startTime:.2f} 秒")
            time.sleep(1)
        evaluator = EvalutionBase()
        evaluator.evaluate(results)
        save_results(results)

        