import requests
from pr_review_system.config import GITHUB_TOKEN

class GitHubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

    def get_prs(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"
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