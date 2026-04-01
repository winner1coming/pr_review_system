import requests
from pr_review_system.review.valid import is_valid_pr
from pr_review_system.github_api.pr_service import filter_files

def get_valid_prs(github_client, owner, repo, max_prs=10):
    valid_prs = []
    page = 1

    while len(valid_prs) < max_prs:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": "all",
            "per_page": 100,
            "page": page
        }

        r = requests.get(url, headers=github_client.headers, params=params)

        if r.status_code != 200:
            print("GitHub API error:", r.text)
            break

        prs = r.json()
        if not prs:
            break

        for pr in prs:
            print(f"检查PR: {pr['number']}")

            files = github_client.get_pr_files(owner, repo, pr["number"])
            files = filter_files(files)
            if not files:
                print(f"PR #{pr['number']} 没有有效的代码文件，跳过")
                continue

            if is_valid_pr(pr):
                valid_prs.append(pr)

            if len(valid_prs) >= max_prs:
                break

        page += 1

    print(f"✅ 有效PR数量: {len(valid_prs)}")
    return valid_prs