import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

MAX_PRS = 2

SUPPORTED_EXTENSIONS = ['.py', '.js', '.java', '.ts', '.vue']