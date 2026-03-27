import csv
import time

def save_results(results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    keys = results[0].keys()
    with open(f"results_{timestamp}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 结果已保存 results_{timestamp}.csv")

def save_eval_results(eval_results):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    keys = eval_results[0].keys()
    with open(f"eval_results_{timestamp}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=keys
        )
        writer.writeheader()
        writer.writerows(eval_results)

    print(f"✅ 评估结果已保存 eval_results_{timestamp}.csv")