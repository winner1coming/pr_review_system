from pr_review_system.github_api.client import GitHubClient
from pr_review_system.llm.client import LLMClient
from pr_review_system.output.writer import save_eval_results, write_summary_to_csv
from pr_review_system.prompt.builder import PromptBuilder
from concurrent.futures import ThreadPoolExecutor
from pr_review_system.backgroup.get_dependency import build_dependency_context
from pr_review_system.backgroup.get_code_sample import build_code_samples
from pr_review_system.prompt.system_prompt import *
from pr_review_system.prompt.user_prompt import *
import time

class BackGround:
    def __init__ (self):
        self.llm = LLMClient()
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()


    def get_background(self, owner, repo):
        # ========== Step 1: 数据准备 ==========
        readme = self.github.get_readme(owner, repo)
        repo_tree = self.github.get_repo_tree(owner, repo)

        # 构造上下文（非LLM）
        dependency_context = build_dependency_context(owner, repo, repo_tree)
        code_sample_context = build_code_samples(owner, repo, repo_tree)

        # ========== Step 2: 并发执行 LLM ==========
        with ThreadPoolExecutor(max_workers=4) as executor:

            futures = {
                "readme_summary": executor.submit(
                    self.llm.review,
                    {
                        "user": build_readme_user_prompt(readme),
                        "system": build_readme_system_prompt()
                    }
                ),
                "tree_summary": executor.submit(
                    self.llm.review,
                    {
                        "user": build_repo_tree_user_prompt(repo_tree),
                        "system": build_repo_tree_system_prompt()
                    }
                ),
                "dependency_summary": executor.submit(
                    self.llm.review,
                    {
                        "user": build_dependency_user_prompt(dependency_context),
                        "system": build_dependency_system_prompt()
                    }
                ),
                "code_summary": executor.submit(
                    self.llm.review,
                    {
                        "user": build_code_sample_user_prompt(code_sample_context),
                        "system": build_code_sample_system_prompt()
                    }
                )
            }
            results = {}
            for key, future in futures.items():
                results[key] = future.result()

        '''summary_for_csv ={
            "readme":(readme, results.get("readme_summary", "")),
            "repo_tree":("\n".join(repo_tree), results.get("tree_summary", "")),
            "dependency":(str(dependency_context), results.get("dependency_summary", "")),
            "code_sample":(str(code_sample_context), results.get("code_summary", ""))
        }'''
        #timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        #write_summary_to_csv(f"{owner}_{repo}_first_test_backgroup_{timestamp}", summary_for_csv)
        # ========== Step 3: 汇总 ==========
        return {
            **results
        }

