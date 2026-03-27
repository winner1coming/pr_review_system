from setuptools import setup, find_packages

setup(
    name="pr_review_system",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "pr-review=pr_review_system.main:main"
        ]
    }
)