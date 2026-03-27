from pr_review_system.review.reviewer import Reviewer

def main():
    repo = input("输入仓库 (owner/repo): ")
    Reviewer().run(repo)