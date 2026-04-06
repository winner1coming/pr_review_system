import csv
import os
import time
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))



def save_results(results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    keys = results[0].keys()
    repo_name = results[0].get("repo", "unknown_repo/unknown_repo")
    owner, repo = repo_name.split("/")
    OUTPUT_DIR = os.path.join(BASE_DIR, "experiment","prompt_divide_results")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{timestamp}_{owner}_{repo}.csv")

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
    OUTPUT_DIR = os.path.join(BASE_DIR, "experiment",f"prompt_divide_{filename_front}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"_{timestamp}_{owner}_{repo}.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(eval_results)

    print(f"✅ 评估结果已保存 {file_path}")


def write_summary_to_csv(file_path, summary_dict):
    OUTPUT_DIR = os.path.join(BASE_DIR, "experiment","prompt_divide_summary")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["item", "before", "after"])
        
        for key, value in summary_dict.items():
            if isinstance(value, tuple) and len(value) == 2:
                writer.writerow([key, str(value[0]), str(value[1])])
            else:
                writer.writerow([key, "", str(value)])