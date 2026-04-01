import csv
import os
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "diff_lang_readme_test","small")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_results(results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    keys = results[0].keys()
    repo_name = results[0].get("repo", "unknown_repo/unknown_repo")
    owner, repo = repo_name.split("/")
    file_path = os.path.join(OUTPUT_DIR, f"results_{timestamp}_{owner}_{repo}.csv")

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 结果已保存 {file_path}")

def save_eval_results(eval_results, filename_front):
    keys = eval_results[0].keys()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    repo = eval_results[0].get("repo", "unknown_repo/unknown_repo")
    owner, repo = repo.split("/")
    file_path = os.path.join(OUTPUT_DIR, f"{filename_front}_{timestamp}_{owner}_{repo}.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(eval_results)

    print(f"✅ 评估结果已保存 {file_path}")