import csv
import time

def save_results(results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"results_{timestamp}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["repo", "pr", "strategy", "review", "commits", "time"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 结果已保存 results_{timestamp}.csv")