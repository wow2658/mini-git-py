import subprocess

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

process = subprocess.Popen(["python", "main.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
stdout, stderr = process.communicate(scenario)

print("--- STANDARD OUTPUT ---")
print(stdout)
if stderr:
    print("--- STANDARD ERROR ---")
    print(stderr)
