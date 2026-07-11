import os
import time
import random
from models import Commit, Repository
from index import InvertedIndex
from algorithms import (
    topological_sort_commits, 
    shortest_path, 
    get_ancestors, 
    merge_sort, 
    quick_sort
)

def cmd_init(repo: Repository, args: list[str]):
    if not args:
        print("Invalid args")
        return
    repo.current_user = args[0]
    repo.branches['main'] = None
    repo.head = 'main'
    print("Initialized repository.")
    print(f"Current branch: {repo.head}")
    print(f"Current user: {repo.current_user}")

def cmd_branch(repo: Repository, args: list[str]):
    if not args:
        print("Branches:")
        for b_name in repo.branches.keys():
            prefix = "* " if b_name == repo.head else "  "
            print(f"{prefix}{b_name}")
        return
    branch_name = args[0]
    if repo.head is None:
        print("Invalid state: HEAD is not set. Run INIT first.")
        return
    current_commit = repo.branches.get(repo.head)
    repo.branches[branch_name] = current_commit
    print(f"Created branch: {branch_name}")

def cmd_switch(repo: Repository, args: list[str]):
    if not args:
        print("Invalid args")
        return
    branch_name = args[0]
    if branch_name not in repo.branches:
        print(f"Unknown branch: {branch_name}")
        return
    repo.head = branch_name
    print(f"Switched to branch: {branch_name}")

def cmd_commit(repo: Repository, idx: InvertedIndex, args: list[str]):
    if not args:
        print("Invalid args")
        return
    if not repo.current_user:
        print("User not set. Please run INIT first.")
        return
    if not repo.head:
        print("HEAD not set.")
        return
        
    message = args[0]
    current_commit_hash = repo.branches.get(repo.head)
    parents = [current_commit_hash] if current_commit_hash else []
    
    new_commit = Commit(message, repo.current_user, parents)
    repo.add_commit(new_commit)
    idx.add_commit(new_commit)
    
    repo.branches[repo.head] = new_commit.hash
    print(f"[{repo.head} {new_commit.hash}] {message}")

def cmd_log(repo: Repository, args: list[str]):
    if not args:
        # 기본 LOG: 위상 정렬 (부모가 먼저 출력)
        ordered_hashes = topological_sort_commits(repo)
        for h in ordered_hashes:
            c = repo.commits[h]
            branches_here = [b for b, bh in repo.branches.items() if bh == h]
            branch_str = f" [{', '.join(branches_here)}]" if branches_here else ""
            print(f"commit {h} ({c.author}, {c.timestamp}){branch_str}")
            print(c.message)
    else:
        arg = args[0]
        if arg.startswith("--sort-by="):
            sort_key = arg.split("=")[1]
            all_commits = list(repo.commits.values())
            if sort_key == "date":
                sorted_commits = merge_sort(all_commits, key=lambda x: x.timestamp)
            elif sort_key == "author":
                sorted_commits = merge_sort(all_commits, key=lambda x: x.author)
            else:
                print("Invalid args")
                return
                
            for c in sorted_commits:
                print(f"commit {c.hash} ({c.author}, {c.timestamp})")
                print(c.message)
        else:
            print("Invalid args")

def cmd_path(repo: Repository, args: list[str]):
    if len(args) != 2:
        print("Invalid args")
        return
    h1, h2 = args[0], args[1]
    if h1 not in repo.commits:
        print(f"Unknown commit: {h1}")
        return
    if h2 not in repo.commits:
        print(f"Unknown commit: {h2}")
        return
        
    path = shortest_path(repo, h1, h2)
    if path:
        print(f"Path: {' -> '.join(path)}")
    else:
        print("No path")

def cmd_ancestors(repo: Repository, args: list[str]):
    if not args:
        print("Invalid args")
        return
    h = args[0]
    if h not in repo.commits:
        print(f"Unknown commit: {h}")
        return
        
    ancestors = get_ancestors(repo, h)
    print("Ancestors:")
    for a in ancestors:
        print(a)

def cmd_search(repo: Repository, idx: InvertedIndex, args: list[str]):
    if not args:
        print("Invalid args")
        return
    arg = args[0]
    
    if arg.startswith("--author="):
        author = arg.split("=")[1]
        results = idx.search_by_author(author)
    else:
        keyword = arg
        results = idx.search_by_keyword(keyword)
        
    print(f"Found {len(results)} commit(s):")
    for h in results:
        c = repo.commits[h]
        print(f"- {h}: {c.message}")

# --- 보너스 과제 ---

def cmd_diff(args: list[str]):
    if len(args) != 2:
        print("Invalid args")
        return
    f1, f2 = args[0], args[1]
    if not os.path.exists(f1) or not os.path.exists(f2):
        print("File not found.")
        return
    
    with open(f1, 'r', encoding='utf-8') as file1:
        lines1 = file1.readlines()
    with open(f2, 'r', encoding='utf-8') as file2:
        lines2 = file2.readlines()
        
    # LCS DP 배열
    m, n = len(lines1), len(lines2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if lines1[i-1] == lines2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                
    # 역추적하여 변경 내역 생성
    i, j = m, n
    diff_res = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and lines1[i-1] == lines2[j-1]:
            diff_res.append("  " + lines1[i-1].rstrip())
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            diff_res.append("+ " + lines2[j-1].rstrip())
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j-1] < dp[i-1][j]):
            diff_res.append("- " + lines1[i-1].rstrip())
            i -= 1
            
    diff_res.reverse()
    for line in diff_res:
        print(line)

def cmd_merge(repo: Repository, idx: InvertedIndex, args: list[str]):
    if len(args) != 1:
        print("Invalid args")
        return
    target_branch = args[0]
    if target_branch not in repo.branches:
        print(f"Unknown branch: {target_branch}")
        return
        
    target_hash = repo.branches[target_branch]
    current_hash = repo.branches.get(repo.head)
    
    if target_hash is None:
        print("Target branch has no commits.")
        return
        
    parents = []
    if current_hash:
        parents.append(current_hash)
    if target_hash and target_hash not in parents:
        parents.append(target_hash)
        
    message = f"Merge branch '{target_branch}' into {repo.head}"
    new_commit = Commit(message, repo.current_user, parents)
    repo.add_commit(new_commit)
    idx.add_commit(new_commit)
    
    repo.branches[repo.head] = new_commit.hash
    print(f"[{repo.head} {new_commit.hash}] {message}")

def cmd_compare_sort(args: list[str]):
    sizes = [100, 1000, 3000]
    if args:
        try:
            sizes = [int(a) for a in args]
        except ValueError:
            print("Invalid args")
            return
            
    print(f"{'Size':>10} | {'Merge Sort (s)':>18} | {'Quick Sort (s)':>18}")
    print("-" * 52)
    for size in sizes:
        arr = [random.randint(0, 100000) for _ in range(size)]
        
        arr_m = arr.copy()
        arr_q = arr.copy()
        
        start = time.time()
        merge_sort(arr_m)
        end_m = time.time() - start
        
        start = time.time()
        quick_sort(arr_q)
        end_q = time.time() - start
        print(f"{size:10} | {end_m:18.6f} | {end_q:18.6f}")

def cmd_help():
    help_text = """
=== Mini Git Commands ===
  init <user_name>           : Initialize repo and set user
  commit "<message>"         : Create a new commit
  branch                     : List all branches
  branch <branch_name>       : Create a new branch
  switch <branch_name>       : Switch to a branch
  log                        : View commit history
  log --sort-by=date         : View history sorted by date
  log --sort-by=author       : View history sorted by author
  path <hash1> <hash2>       : Find shortest path between commits
  ancestors <hash>           : List all ancestors of a commit
  search <keyword>           : Search commits by keyword
  search --author=<name>     : Search commits by author
  diff <file1> <file2>       : Compare two files (Bonus)
  merge <branch_name>        : Merge a branch (Bonus)
  compare-sort               : Compare sorting performance (Bonus)
  help                       : Show this help message
  exit, quit                 : Exit the program
=========================
"""
    print(help_text.strip())
