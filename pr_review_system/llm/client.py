import requests
from pr_review_system.config import DEEPSEEK_API_KEY

class LLMClient:

    def review(self, prompt,temperature=0.3):
        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ],
            "temperature": temperature
        }

        r = requests.post(url, json=data, headers=headers)

        if r.status_code != 200:
            return f"ERROR: {r.text}"

        return r.json()["choices"][0]["message"]["content"]