import uuid
from datetime import datetime

class Commit:
    """
    커밋 정보를 담는 노드 클래스.
    DAG (방향성 비순환 그래프)의 노드 역할을 합니다.
    """
    def __init__(self, message: str, author: str, parents: list[str]):
        # 중복이 발생하지 않도록 UUID 활용, 편의상 앞 6자리 사용
        self.hash = uuid.uuid4().hex[:6]
        self.message = message
        self.author = author
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.parents = parents  # 부모 커밋들의 hash 목록

    def __str__(self):
        return f"commit {self.hash} ({self.author}, {self.timestamp})\n{self.message}"


class Repository:
    """
    Mini Git 저장소 상태를 관리하는 클래스.
    메모리 상에서 커밋, 브랜치, HEAD, 사용자 정보를 관리합니다.
    """
    def __init__(self):
        self.commits: dict[str, Commit] = {}  # hash -> Commit
        self.branches: dict[str, str] = {}    # branch_name -> commit_hash
        self.head: str | None = None          # 현재 체크아웃된 브랜치 이름
        self.current_user: str | None = None  # 현재 사용자 이름

    def get_head_commit(self) -> Commit | None:
        """현재 HEAD가 가리키는 커밋을 반환합니다."""
        if not self.head or self.head not in self.branches:
            return None
        commit_hash = self.branches[self.head]
        return self.commits.get(commit_hash)

    def add_commit(self, commit: Commit):
        """저장소에 새 커밋을 추가합니다."""
        self.commits[commit.hash] = commit
