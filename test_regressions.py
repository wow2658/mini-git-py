import contextlib
import io
from itertools import product
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from algorithms import myers_diff
from commands import cmd_init, cmd_branch, cmd_commit, cmd_switch
from index import InvertedIndex
from models import Repository


class GitRegressionTests(unittest.TestCase):
    def assert_valid_minimal_diff(self, before, after):
        diff = myers_diff(before, after)
        self.assertEqual([s[2:] for s in diff if s[:2] in ('  ', '- ')],
                         [s.rstrip() for s in before], diff)
        self.assertEqual([s[2:] for s in diff if s[:2] in ('  ', '+ ')],
                         [s.rstrip() for s in after], diff)
        # Independent insert/delete edit-distance oracle for short sequences.
        costs = list(range(len(after) + 1))
        for i, left in enumerate(before, 1):
            row = [i]
            for j, right in enumerate(after, 1):
                row.append(costs[j - 1] if left == right else min(costs[j], row[-1]) + 1)
            costs = row
        self.assertEqual(sum(s[:2] in ('+ ', '- ') for s in diff), costs[-1], diff)

    def test_replacement_diff(self):
        self.assert_valid_minimal_diff(['a\n', 'b\n'], ['a\n', 'c\n'])
        self.assertEqual(myers_diff(['a\n', 'b\n'], ['a\n', 'c\n']), ['  a', '- b', '+ c'])

    def test_exhaustive_short_diffs(self):
        sequences = [list(items) for n in range(5) for items in product(['a\n', 'b\n'], repeat=n)]
        for before in sequences:
            for after in sequences:
                with self.subTest(before=before, after=after):
                    self.assert_valid_minimal_diff(before, after)

    def test_unicode_diff(self):
        self.assert_valid_minimal_diff(['안녕\n', 'café\n', '끝\n'], ['안녕\n', '새 줄\n', '끝\n'])

    def test_duplicate_branch_preserves_tip_head_and_commits(self):
        repo, idx = Repository(), InvertedIndex()
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_init(repo, ['tester'])
            cmd_commit(repo, idx, ['root'])
            cmd_branch(repo, ['feature'])
            cmd_switch(repo, ['feature'])
            cmd_commit(repo, idx, ['feature work'])
            cmd_switch(repo, ['main'])
        branches, commits = repo.branches.copy(), repo.commits.copy()
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            cmd_branch(repo, ['feature'])
            cmd_branch(repo, ['main'])
        self.assertEqual(repo.branches, branches)
        self.assertEqual(repo.commits, commits)
        self.assertEqual(repo.head, 'main')
        self.assertIn('Branch already exists: feature', stream.getvalue())

    def test_cli_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            before, after = Path(tmp) / 'before.txt', Path(tmp) / 'after.txt'
            before.write_text('a\nb\n')
            after.write_text('a\nc\n')
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('main.py'))],
                                    input=f'diff "{before}" "{after}"\nexit\n',
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('  a\n- b\n+ c\n', result.stdout)

    def test_smoke_script_uses_current_python_from_other_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('test_run.py'))],
                                    cwd=tmp, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Found 1 commit(s):', result.stdout)
        self.assertNotIn('Traceback', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
