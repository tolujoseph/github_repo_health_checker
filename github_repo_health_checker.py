import requests
from tabulate import tabulate

# --- CONFIG ---
GITHUB_TOKEN = None  # Optional: add a GitHub token if hitting rate limits

HEADERS = {
    "Accept": "application/vnd.github+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def check_repo_health(owner, repo):
    print(f"[INFO] Checking health of: {owner}/{repo}")

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_data = requests.get(base_url, headers=HEADERS).json()

    if 'message' in repo_data and repo_data['message'] == 'Not Found':
        print("[ERROR] Repository not found.")
        return

    # Metadata
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    open_issues = repo_data.get("open_issues_count", 0)
    last_push = repo_data.get("pushed_at", "N/A")
    size_kb = repo_data.get("size", 0)

    # File presence
    files = requests.get(base_url + "/contents", headers=HEADERS).json()
    filenames = [f['name'].lower() for f in files if isinstance(f, dict)]

    has_readme = "readme.md" in filenames
    has_license = "license" in filenames
    has_contributing = "contributing.md" in filenames
    has_tests = any("test" in name or "tests" in name for name in filenames)

    score = sum([has_readme, has_license, has_contributing, has_tests]) * 25

    report = [
        ["Stars", stars],
        ["Forks", forks],
        ["Open Issues", open_issues],
        ["Last Push", last_push],
        ["Repo Size (KB)", size_kb],
        ["README.md", "✅" if has_readme else "❌"],
        ["LICENSE", "✅" if has_license else "❌"],
        ["CONTRIBUTING.md", "✅" if has_contributing else "❌"],
        ["Tests Folder", "✅" if has_tests else "❌"],
        ["Health Score", f"{score}/100"]
    ]

    print(tabulate(report, headers=["Metric", "Value"], tablefmt="github"))

def main():
    repo_input = input("Enter GitHub repo (owner/repo): ").strip()
    if '/' not in repo_input:
        print("[ERROR] Input must be in the format owner/repo")
        return

    owner, repo = repo_input.split('/')
    check_repo_health(owner, repo)

if __name__ == "__main__":
    main()
