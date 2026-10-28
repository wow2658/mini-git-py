import subprocess
import sys
from pathlib import Path

scenario = """init kim
commit "first commit"
commit "second commit"
branch feature-login
branch
switch feature-login
commit "login form added"
log
switch main
search "login"
exit
"""

def main():
    result = subprocess.run(
        [sys.executable, '-B', str(Path(__file__).with_name('main.py'))],
        input=scenario, capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    print("--- STANDARD OUTPUT ---")
    print(result.stdout)
    if result.stderr:
        print("--- STANDARD ERROR ---")
        print(result.stderr)
    if result.returncode:
        return result.returncode
    expected = ["Initialized repository.", "Created branch: feature-login", "Found 1 commit(s):"]
    if any(text not in result.stdout for text in expected):
        print("Smoke test failed: expected scenario output is missing.", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
