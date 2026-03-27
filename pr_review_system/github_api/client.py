import requests
from pr_review_system.config import GITHUB_TOKEN

class GitHubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

    def get_prs(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
        return requests.get(url, headers=self.headers).json()

    def get_pr_files(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []

        return r.json()

    def get_readme(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            return ""

        import base64
        return base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
    
    def get_pr_commits(self,owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    # 获取PR的评论信息,用于评估LLM审查结果的合理性
    def get_review_comments(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    def get_reviews(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []
    
        return r.json()
    
    def get_issue_comments(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            return []

        return r.json()