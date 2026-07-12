import sys
import shlex
from models import Repository
from index import InvertedIndex
from commands import (
    cmd_init, cmd_branch, cmd_switch, cmd_commit,
    cmd_log, cmd_path, cmd_ancestors, cmd_search,
    cmd_diff, cmd_merge, cmd_compare_sort, cmd_compare_diff, cmd_help
)

def main():
    repo = Repository()
    idx = InvertedIndex()
    
    print("Welcome to Mini Git!")
    print("Type 'help' to see available commands. Type 'exit' or 'quit' to close.")
    
    while True:
        try:
            user_input = input("mini-git> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
            
        if not user_input:
            continue
            
        try:
            # shlex.split을 통해 따옴표(")로 묶인 문자열을 올바르게 파싱합니다.
            tokens = shlex.split(user_input)
        except ValueError as e:
            print(f"Error parsing input: {e}")
            continue
            
        cmd = tokens[0].lower()
        args = tokens[1:]
        
        if cmd in ['exit', 'quit']:
            break
        elif cmd == 'help':
            cmd_help()
        elif cmd == 'init':
            cmd_init(repo, args)
        elif cmd == 'branch':
            cmd_branch(repo, args)
        elif cmd == 'switch':
            cmd_switch(repo, args)
        elif cmd == 'commit':
            cmd_commit(repo, idx, args)
        elif cmd == 'log':
            cmd_log(repo, args)
        elif cmd == 'path':
            cmd_path(repo, args)
        elif cmd == 'ancestors':
            cmd_ancestors(repo, args)
        elif cmd == 'search':
            cmd_search(repo, idx, args)
        elif cmd == 'diff':
            cmd_diff(args)
        elif cmd == 'merge':
            cmd_merge(repo, idx, args)
        elif cmd == 'compare-sort':
            cmd_compare_sort(args)
        elif cmd == 'compare-diff':
            cmd_compare_diff(args)
        else:
            print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
