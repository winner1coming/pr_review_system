import csv
import time

def save_results(results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    keys = results[0].keys()
    repo_name = results[0].get("repo", "unknown_repo/unknown_repo")
    owner, repo = repo_name.split("/")
    with open(f"results_{timestamp}_{owner}_{repo}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 结果已保存 results_{timestamp}_{owner}_{repo}.csv")

def save_eval_results(eval_results, filename_front):
    keys = eval_results[0].keys()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    repo = eval_results[0].get("repo", "unknown_repo/unknown_repo")
    owner, repo = repo.split("/")
    with open(f"{filename_front}_{timestamp}_{owner}_{repo}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(eval_results)

    print(f"✅ 评估结果已保存 {filename_front}_{timestamp}_{owner}_{repo}.csv")