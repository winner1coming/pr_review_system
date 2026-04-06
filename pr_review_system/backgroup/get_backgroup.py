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
time.sleep(1)

class BackGround:
    def __init__ (self):
        self.llm = LLMClient()
        self.github = GitHubClient()
        self.prompt_builder = PromptBuilder()
        self.cache = {}


    def get_background(self, owner, repo):
        # ========== Step 1: 数据准备 ==========
        key = f"{owner}/{repo}"
        if key in self.cache:
            print("使用缓存的背景信息")
            return self.cache[key]
        readme = self.github.get_readme(owner, repo)
        repo_tree = self.github.get_repo_tree(owner, repo)
        self.cache[key] = repo_tree  # 缓存结果

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

        # ========== Step 3: 汇总 ==========
        return {
            **results
        }
    
def format_readme_summary(data):

    summary = data.get("project_summary", "未知")
    domain = data.get("application_domain", "未知")
    features = data.get("key_features", [])
    scenarios = data.get("usage_scenarios", [])

    features_str = "、".join(features) if features else "未知"
    scenarios_str = "、".join(scenarios) if scenarios else "未知"

    return f"""该项目主要用于{summary}，属于{domain}领域。
其核心功能包括：{features_str}。
典型应用场景包括：{scenarios_str}。"""

def format_architecture_summary(data):
    print(f"格式化架构摘要：{data}, type: {type(data)}")
    modules = data.get("core_modules", [])
    hierarchy = data.get("module_hierarchy", "未知")
    responsibilities = data.get("module_responsibilities", {})
    pattern = data.get("architecture_pattern", "未知")

    modules_str = "、".join(modules) if modules else "未知"

    resp_str = "；".join(
        [f"{k}负责{v}" for k, v in responsibilities.items()]
    ) if responsibilities else "未知"

    return f"""该项目采用{pattern}架构，核心模块包括{modules_str}。
模块层级结构为：{hierarchy}。
各模块职责如下：{resp_str}。"""

def format_dependency_summary(data):
    langs = data.get("programming_languages", [])
    frameworks = data.get("frameworks", [])
    infra = data.get("infrastructure_components", [])
    arch_type = data.get("architecture_type", "未知")

    langs_str = "、".join(langs) if langs else "未知"
    fw_str = "、".join(frameworks) if frameworks else "未知"
    infra_str = "、".join(infra) if infra else "未知"

    return f"""该项目主要使用{langs_str}开发，基于{fw_str}等框架。
系统依赖的基础组件包括：{infra_str}。
整体系统类型为{arch_type}。"""

def format_code_style_summary(data):
    naming = data.get("naming_convention", "未知")
    comment = data.get("comment_style", "未知")
    structure = data.get("code_structure", "未知")
    error = data.get("error_handling", "未知")
    quality = data.get("code_quality_characteristics", [])

    quality_str = "、".join(quality) if quality else "未知"

    return f"""该项目代码主要采用{naming}命名规范。
注释风格为：{comment}。
代码结构方面：{structure}。
错误处理方式为：{error}。
整体代码质量特征包括：{quality_str}。"""

