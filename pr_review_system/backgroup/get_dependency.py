from pr_review_system.backgroup.dependence_files import DEPENDENCY_FILES
from pr_review_system.github_api.client import GitHubClient


def get_dependency_files(repo_tree):
        found_files = []

        for file_path in repo_tree:
            filename = file_path.split("/")[-1]

            for lang,files in DEPENDENCY_FILES.items():
                if filename in files:
                    found_files.append({
                        "path": file_path,
                        "type": lang
                    })

        return found_files

def build_dependency_context(owner, repo, repo_tree):
        dependency_files = get_dependency_files(repo_tree)

        if not dependency_files:
            return []
        dependency = []
        github_client = GitHubClient()
        for file in dependency_files:
            content = github_client.fetch_file_content(owner, repo, file["path"])
            dependency.append({
                "file": file["path"],
                "type": file["type"],
                "content": content
            })

        return dependency