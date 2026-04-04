import time

import requests
from pr_review_system.config import GITHUB_TOKEN

class GitHubClient:
    headers = {}
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

    def get_prs(self, owner, repo, page):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": "all",
            "per_page": 100,
            "page": page
        }
        time.sleep(1)
        x = requests.get("https://api.github.com/rate_limit", headers=self.headers)
        print(x.json()["resources"]["core"]["remaining"])
        r = requests.get(url, headers=self.headers, params=params)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []

        return r.json()

    def get_pr_files(self, owner, repo, pr_number):
        time.sleep(1)

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []

        return r.json()

    def get_readme(self, owner, repo):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            return ""

        import base64
        return base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
    
    def get_pr_commits(self,owner, repo, pr_number):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    # 获取PR的评论信息,用于评估LLM审查结果的合理性
    def get_review_comments(self, owner, repo, pr_number):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    def get_reviews(self, owner, repo, pr_number):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    def get_issue_comments(self, owner, repo, pr_number):
        time.sleep(1)
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []

        return r.json()
    
    def get_repo_tree(self, owner, repo):
        """
        获取仓库完整目录树（递归）
        返回：包含文件路径的列表
        """
        time.sleep(1)

        # ---------- Step 1: 获取默认分支 ----------
        url_repo = f"https://api.github.com/repos/{owner}/{repo}"
        r_repo = requests.get(url_repo, headers=self.headers)
        if r_repo.status_code != 200:
            raise ValueError(f"Failed to get repo info: {r_repo.status_code} {r_repo.text}")
        repo_info = r_repo.json()
        default_branch = repo_info.get("default_branch")
        if not default_branch:
            raise ValueError(f"Cannot determine default branch for {owner}/{repo}")

        # ---------- Step 2: 获取树 ----------
        url_tree = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        r_tree = requests.get(url_tree, headers=self.headers)
        if r_tree.status_code != 200:
            raise ValueError(f"Failed to get repo tree: {r_tree.status_code} {r_tree.text}")
        
        data = r_tree.json()

        # ---------- Step 3: 检查返回结构 ----------
        if "tree" not in data:
            raise ValueError(f"No 'tree' in response: {data}")

        # ---------- Step 4: 返回文件路径列表 ----------
        paths = [item["path"] for item in data["tree"]]
        return paths
    
    def fetch_file_content(self,owner, repo, path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        time.sleep(1)
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            return ""

        import base64
        return base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")