import random
from pr_review_system.github_api.client import GitHubClient

def get_code_sample_files(repo_tree):
        candidates = []
        for path in repo_tree:
            if path.endswith((".py", ".js", ".java", ".ts", ".vue", ".go", ".cpp", ".c", ".cs", ".rb", ".php",".rs")):
                if any(keyword in path.lower() for keyword in [
                    "test","mock","example"
                ]):
                    continue
                
                if any(keyword in path.lower() for keyword in [
                    "src","lib","core","main","app","service","controller"
                ]):
                    candidates.append(path)
        
        if len(candidates) <= 3:
            return candidates
        return random.sample(candidates, 3)

def fetch_code_samples(owner, repo, file_paths):
    samples = []
    github_client = GitHubClient()
    for path in file_paths:
        content = github_client.fetch_file_content(owner, repo, path)

        if not content:
            continue

        samples.append({
            "path": path,
            "content": content
        })

    return samples
    
def slice_code(content, max_lines=100):
    lines = content.split("\n")
    n = len(lines)

    if n <= max_lines:
        return content

    part = max_lines // 3

    return "\n".join(
        lines[:part] +                  # 开头（import + 风格）
        lines[n//2:n//2+part] +         # 中间（逻辑）
        lines[-part:]                  # 结尾（辅助函数）
    )

def build_code_samples(owner, repo, repo_tree):
    file_paths = get_code_sample_files(repo_tree)

    raw_samples = fetch_code_samples(owner, repo, file_paths)

    final_samples = []

    for sample in raw_samples:
        sliced = slice_code(sample["content"])

        final_samples.append({
            "file": sample["path"],
            "snippet": sliced
        })

    return final_samples