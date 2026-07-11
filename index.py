class InvertedIndex:
    """
    검색 성능 향상을 위한 역색인(Inverted Index) 클래스.
    모든 커밋을 순회하지 않고도 키워드나 작성자로 빠르게 검색할 수 있습니다.
    """
    def __init__(self):
        self.keyword_index: dict[str, list[str]] = {} # keyword -> list of commit hashes
        self.author_index: dict[str, list[str]] = {}  # author -> list of commit hashes

    def add_commit(self, commit):
        """커밋 생성 시 역색인을 갱신합니다."""
        # 1. 키워드 기반 인덱스 갱신
        # 커밋 메시지를 공백 기준으로 분리하고 소문자로 정규화
        tokens = commit.message.split()
        for token in tokens:
            token_lower = token.lower()
            if token_lower not in self.keyword_index:
                self.keyword_index[token_lower] = []
            if commit.hash not in self.keyword_index[token_lower]:
                self.keyword_index[token_lower].append(commit.hash)

        # 2. 작성자 기반 인덱스 갱신
        if commit.author not in self.author_index:
            self.author_index[commit.author] = []
        if commit.hash not in self.author_index[commit.author]:
            self.author_index[commit.author].append(commit.hash)

    def search_by_keyword(self, keyword: str) -> list[str]:
        """키워드가 포함된 커밋의 해시 목록을 반환합니다."""
        return self.keyword_index.get(keyword.lower(), [])

    def search_by_author(self, author: str) -> list[str]:
        """특정 작성자의 커밋 해시 목록을 반환합니다."""
        return self.author_index.get(author, [])
