from pr_review_system.github_api.client import GitHubClient
from pr_review_system.github_api.pr_service import filter_files
from pr_review_system.utils.diff_utils import extract_diff
from pr_review_system.prompt.builder import PromptBuilder
from pr_review_system.llm.client import LLMClient
from pr_review_system.output.writer import save_results
from pr_review_system.config import MAX_PRS

import time

class Reviewer:

    def __init__(self):
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

    def run(self, repo_name):
        owner, repo = repo_name.split("/")

        prs = self.github.get_prs(owner, repo)
        readme = self.github.get_readme(owner, repo)

        results = []

        for pr in prs[:MAX_PRS]:
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

            for strategy in ["baseline", "with_readme"]:
                print("👉 策略:", strategy)

                prompt = self.prompt_builder.build(strategy, diff, commit_info, readme)
                review = self.llm.review(prompt)
                results.append({
                    "repo": repo_name,
                    "pr": pr_number,
                    "strategy": strategy,
                    "review": review,
                    "commits": commit_info,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })

                time.sleep(1)

            save_results(results)

        