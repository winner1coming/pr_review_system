import time

import requests
from pr_review_system.review.valid import is_valid_pr
from pr_review_system.github_api.pr_service import filter_files

def get_valid_prs(github_client, owner, repo, max_prs=10):
    time.sleep(1)  # 避免过快请求导致速率限制
    valid_prs = []
    page = 1

    while len(valid_prs) < max_prs:
        prs = github_client.get_prs(owner, repo, page)
        if not prs:
            break

        for pr in prs:
            print(f"检查PR: {pr['number']}")
            pr_number = pr["number"]
            files = github_client.get_pr_files(owner, repo, pr_number)
            files = filter_files(files)
            if not files:
                print(f"PR #{pr['number']} 没有有效的代码文件，跳过")
                continue
            comments = github_client.get_review_comments(owner, repo, pr_number)
            people_reviews = github_client.get_reviews(owner, repo, pr_number)
            issue_comments = github_client.get_issue_comments(owner, repo, pr_number)
            review_comments = []
            review_comments += [c["body"] for c in comments if c["body"]]
            review_comments += [r["body"] for r in people_reviews if r["body"]]
            review_comments += [c["body"] for c in issue_comments if c["body"]]


            if not review_comments:
                print("跳过（无评论）")
                continue
            if is_valid_pr(pr):
                valid_prs.append({"pr": pr, "review_comments": review_comments})

            if len(valid_prs) >= max_prs:
                break

        page += 1

    print(f"✅ 有效PR数量: {len(valid_prs)}")
    return valid_prs