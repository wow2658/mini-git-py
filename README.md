# Mini Git

CLI 기반의 Mini Git 구현 프로젝트이다. 커밋 그래프, 정렬, 최단 경로, 역색인 검색 등의 자료구조와 알고리즘을 활용하여 Git의 핵심 동작을 시뮬레이션한다.

## 실행 방법

```bash
python main.py
```

명령 프롬프트(`mini-git> `)가 나타나면 아래 명령어들을 사용할 수 있다.

## 지원 명령어

- `init <user_name>`: 저장소 초기화, `main` 브랜치 생성, 사용자 설정
- `commit "<message>"`: 새 커밋 생성 (메시지 공백 포함 시 따옴표 `""` 사용)
- `branch`: 전체 브랜치 목록 출력
- `branch <branch_name>`: 현재 `HEAD`를 가리키는 새 브랜치 생성
- `switch <branch_name>`: 지정한 브랜치로 `HEAD` 이동
- `log`: 위상 정렬을 기반으로 커밋 이력 출력 (최신/자식 커밋 먼저 출력)
- `log --sort-by=date`: 날짜 순서대로 커밋 정렬 출력 (Merge Sort 기반)
- `log --sort-by=author`: 작성자 순서대로 커밋 정렬 출력 (Merge Sort 기반)
- `path <commit_hash_1> <commit_hash_2>`: 두 커밋 간의 무방향 최단 경로 출력
- `ancestors <commit_hash>`: 지정한 커밋의 모든 조상 출력
- `search <keyword>`: 키워드가 포함된 커밋 검색 (역색인 기반)
- `search --author=<name>`: 특정 작성자의 커밋 검색 (역색인 기반)

### 보너스 기능
- `diff <file1> <file2>`: 두 텍스트 파일 내용 비교 (간단한 diff)
- `merge <branch_name>`: 대상 브랜치와 현재 브랜치를 부모로 하는 병합 커밋 생성
- `compare-sort`: 정렬 알고리즘 2개(병합 정렬, 퀵 정렬)의 성능 비교

### 유틸리티
- `help`: 전체 명령어 도움말 출력
- `exit` 또는 `quit`: 프로그램 종료

## 🚀 실행 예시 (Usage Scenario)

실제 REPL 환경에서 테스트하고 실습할 수 있는 명령어 시퀀스와 그에 따른 예상 결과이다.

### 1. 저장소 초기화
```text
mini-git> init kim
Initialized repository.
Current branch: main
Current user: kim
```

### 2. 기본 커밋 생성
```text
mini-git> commit "first commit"
[main 1a2b3c] first commit

mini-git> commit "second commit"
[main 4d5e6f] second commit
```

### 3. 브랜치 생성 및 이동
```text
mini-git> branch feature-login
Created branch: feature-login

mini-git> branch
Branches:
* main
  feature-login

mini-git> switch feature-login
Switched to branch: feature-login

mini-git> commit "login form added"
[feature-login 7g8h9i] login form added
```

### 4. 로그 확인 (위상 정렬)
```text
mini-git> log
commit 7g8h9i (kim, 2026-07-11 10:00:00) [feature-login]
login form added
commit 4d5e6f (kim, 2026-07-11 09:50:00) [main]
second commit
commit 1a2b3c (kim, 2026-07-11 09:40:00)
first commit
```

### 5. 병합 (Merge)
```text
mini-git> switch main
Switched to branch: main

mini-git> merge feature-login
[main 0j1k2l] Merge branch 'feature-login' into main
```

### 6. 역색인 검색 (Search)
```text
mini-git> search "login"
Found 1 commit(s):
- 7g8h9i: login form added
```

### 7. 경로 탐색 (Path)
*참고: 해시값은 실행 시마다 무작위로 생성되므로, 화면에 출력된 실제 해시값을 입력해야 한다.*
```text
mini-git> path 1a2b3c 7g8h9i
Path: 1a2b3c -> 4d5e6f -> 7g8h9i
```

## 기술 스택 및 구조
- Python 3.10+ 표준 라이브러리 (정렬 및 그래프 외부 라이브러리 미사용)
- `models.py`: `Commit` (DAG 노드), `Repository` (저장소 상태)
- `algorithms.py`: `merge_sort`, `quick_sort`, `topological_sort_commits`, `shortest_path` 등
- `index.py`: `InvertedIndex` (빠른 키워드 및 작성자 검색 지원)
- `commands.py`: 각 명령어에 대응하는 핸들러 로직
- `main.py`: `shlex` 모듈을 이용한 REPL 인터페이스 구성

## 🎯 요구사항 구현 대응표 (코드 매핑)

과제에서 요구한 핵심 기능들이 실제 소스 코드에 어떻게 구현되었는지 1:1로 대응시킨 내역이다. 코드 제목의 링크를 클릭하면 해당 파일의 구현부로 즉시 이동할 수 있다.

### 1. 저장소 및 브랜치 관리
* **`INIT` (저장소 초기화)**: [commands.py:14](commands.py#L14-L23)
  ```python
  def cmd_init(repo: Repository, args: list[str]):
      repo.current_user = args[0]
      repo.branches['main'] = None
      repo.head = 'main'
  ```
* **`BRANCH` (브랜치 생성/조회)**: [commands.py:25](commands.py#L25-L38)
  ```python
  def cmd_branch(repo: Repository, args: list[str]):
      # 브랜치 목록 출력 및 HEAD 포인터를 복사하여 새 브랜치 생성
      current_commit = repo.branches.get(repo.head)
      repo.branches[branch_name] = current_commit
  ```
* **`COMMIT` (커밋 생성)**: [commands.py:51](commands.py#L51-L71)
  ```python
  def cmd_commit(repo: Repository, idx: InvertedIndex, args: list[str]):
      new_commit = Commit(message, repo.current_user, parents)
      repo.add_commit(new_commit)
      repo.branches[repo.head] = new_commit.hash # HEAD 포인터 전진
  ```

### 2. 커밋 로그 및 탐색
* **`LOG` (위상 정렬)**: [algorithms.py:120](algorithms.py#L120-L151)
  ```python
  def topological_sort_commits(repo) -> list[str]:
      # 진입 차수(in-degree)와 자식 노드 매핑을 통한 위상 정렬 구현
      in_degree = {c: len(repo.commits[c].parents) for c in repo.commits}
      ...
  ```
* **`PATH` (최단 경로, BFS)**: [algorithms.py:61](algorithms.py#L61-L117)
  ```python
  def shortest_path(repo, hash1: str, hash2: str) -> list[str] | None:
      queue = [(hash1, [hash1])] # 무방향 그래프 탐색(BFS)
      ...
  ```

### 3. 검색 및 정렬
* **`SEARCH` (역색인 검색)**: [index.py:28](index.py#L28-L35)
  ```python
  class InvertedIndex:
      def search_by_keyword(self, keyword: str) -> list[str]:
          # O(1)에 가까운 역색인 딕셔너리 탐색
          return list(self.keyword_index.get(keyword, set()))
  ```
* **`LOG --sort-by` (병합 정렬)**: [algorithms.py:1](algorithms.py#L1-L18)
  ```python
  def merge_sort(arr, key=lambda x: x):
      # 파이썬 내장 sort() 대신 직접 구현한 병합 정렬 사용
      mid = len(arr) // 2
      ...
  ```

### 4. CLI 인터페이스
* **무한 루프 REPL 및 명령 파싱**: [main.py:18](main.py#L18-L69)
  ```python
  while True:
      user_input = input("mini-git> ").strip()
      tokens = shlex.split(user_input) # 띄어쓰기 포함 문자열 완벽 파싱
      cmd = tokens[0].lower()
  ```

---

## 💡 과제 미션 분석: Git의 핵심 원리와 알고리즘적 의의

이 프로젝트는 Git이라는 거대한 블랙박스의 뚜껑을 열고, 그 안의 핵심 부품들을 바닥부터 조립하며 컴퓨터 공학의 꽃인 **'그래프 이론과 탐색 알고리즘'**을 실생활에 적용해 보는 거대한 실습장이다.

### 1. "커밋 하나에는 그래프 자료구조와 해시가 담겨 있다"의 진짜 의미
Git에서 커밋을 할 때마다 내부적으로 어떤 일이 일어나는지 들여다보면 이 말은 비유가 아니라 100% 물리적인 사실이다.

#### ① 해시(Hash)가 담겨 있다는 것
Git은 커밋이 생성될 때 파일의 내용, 작성자, 작성 시간, 커밋 메시지 등을 모두 뭉쳐서 SHA-1 해시 함수에 통과시킨다.
* 그 결과로 `1a2b3c4d5e...` 같은 40자리의 고유한 문자열(해시값)이 탄생한다.
* 이 해시값은 단순한 이름표가 아니라 **"이 커밋의 내용이 단 1비트라도 바뀌면 해시값도 완전히 달라진다"**는 무결성을 보장하는 절대적인 식별자(주민번호)이다.

#### ② 그래프 자료구조가 담겨 있다는 것 (핵심)
가장 중요한 것은 커밋 내부 데이터에 **"내 부모 커밋의 해시값(Parent Hash)"**이 적혀 있다는 점이다.
* 첫 번째 커밋은 부모가 없다.
* 두 번째 커밋은 자기 자신 안에 '첫 번째 커밋의 해시값'을 가리키는 포인터를 저장한다.
* 이렇게 "내가 누구의 자식인지"를 가리키는 화살표들이 모이면, 점(커밋)과 선(부모를 가리키는 화살표)으로 이루어진 **단방향 비순환 그래프(DAG, Directed Acyclic Graph)**가 완벽하게 형성된다.
* 결론적으로 Git의 이력(History)은 파일들의 단순한 나열이 아니라, **"해시값을 노드(점)로 삼고, 부모 포인터를 간선(선)으로 삼는 거대한 그래프 자료구조 그 자체"**이다.

### 2. rebase, merge, cherry-pick은 무엇이고, 어떻게 다르게 보이는가?
일반적인 개발자들은 이 명령어들을 "브랜치를 합치는 마법의 버튼" 정도로 외워서 쓴다. 하지만 커밋이 **'그래프의 노드(점)'**라는 것을 깨닫고 나면, 이 명령어들은 단순히 **"그래프 조작(Graph Manipulation) 알고리즘"**으로 다르게 보이기 시작한다.

#### ① Merge (병합)
* **일반적인 활용 관점**: "내 브랜치에 남의 브랜치 코드를 합치는 명령어"
* **그래프 관점의 시선**: "부모 노드가 2개인 특수 노드(Merge Commit)를 생성하여, 갈라져 있던 두 개의 부분 그래프(Subgraph) 경로를 하나로 합치는 작업"
* **알고리즘 연결점**: 두 브랜치를 병합할 때 Git은 두 브랜치의 공통 조상(Lowest Common Ancestor, LCA) 노드를 찾아야 한다. 공통 조상을 기준으로 무엇이 바뀌었는지(3-way merge) 비교해야 하기 때문이다. 즉, 트리/그래프에서 공통 조상을 찾는 알고리즘 역량이 그대로 사용된다.

#### ② Rebase (재배치)
* **일반적인 활용 관점**: "커밋 히스토리를 한 줄로 깔끔하게 펴주는 명령어"
* **그래프 관점의 시선**: "그래프의 특정 가지(Branch)를 싹둑 잘라내어, 다른 노드의 끝트머리에 **새로운 화살표(부모 포인터)를 연결하여 이식(Grafting)**하는 작업"
* **알고리즘 연결점**: 싹둑 잘라낸 커밋들을 새 위치에 붙일 때, 부모가 바뀌었으므로 해시값도 완전히 새로 계산되어 새로운 노드들이 생성된다. 이는 그래프 순회(DFS/BFS)를 통해 대상 노드들을 추출하고, 순서대로 복제하여 새로운 그래프 줄기를 구축하는 알고리즘과 직결된다.

#### ③ Cherry-pick (체리픽)
* **일반적인 활용 관점**: "다른 브랜치에서 내가 원하는 커밋 딱 하나만 복사해 오는 명령어"
* **그래프 관점의 시선**: "그래프 내의 특정 노드 하나가 가진 변경 사항(Delta)만 추출하여, 현재 HEAD 노드의 자식으로 **새로운 노드를 복제(Clone)**하는 작업"
* **알고리즘 연결점**: 거대한 그래프 전체를 조작하지 않고, 특정 해시(노드)를 검색하여 그 차잇값 연산만 수행한 뒤 현재 노드에 덧붙이는 '상태 전이(State Transition)' 응용으로 볼 수 있다.

### 3. 사용되는 정확한 자료구조: DAG (단방향 비순환 그래프)
그래프의 종류는 무수히 많지만, Git의 뼈대를 이루는 자료구조는 정확히 **DAG(Directed Acyclic Graph)**이다.
* **단방향(Directed)**: 현재 커밋은 항상 자신의 과거(부모 커밋)를 가리킨다. 화살표의 방향이 명확하다.
* **비순환(Acyclic)**: 시간이 거꾸로 흘러 과거의 커밋이 미래의 커밋을 가리킬 수는 없다. 즉, 화살표를 따라가다 보면 뱅글뱅글 도는 무한 루프(Cycle)가 절대 발생하지 않는다.

**💡 브랜치의 실체**
우리가 흔히 말하는 "브랜치를 딴다"라는 행위는 물리적인 폴더를 복사하는 것이 아니다. 이 거대한 DAG 그래프 위에서 **특정 노드(해시값)를 가리키는 41바이트짜리 가벼운 포인터(스티커) 하나를 붙이는 것**에 불과하다. 이것이 Git이 브랜치를 0.1초 만에 만드는 이유이다.

### 4. 사용되는 핵심 탐색 알고리즘 3대장
이 DAG 위에서 Git 명령어를 칠 때마다 돌아가는 구체적인 알고리즘은 다음과 같다.

#### ① 최소 공통 조상 (LCA, Lowest Common Ancestor)
* **어디에 쓰이나?**: `git merge` (병합)
* **왜 필요한가?**: 갈라져서 병렬로 작업하던 두 브랜치(A, B)를 하나로 합치려면, 컴퓨터는 두 브랜치가 **"가장 마지막으로 똑같았던 과거의 시점(공통 부모 노드)"**이 언제인지 찾아야 한다. 이 LCA 노드를 찾아야만 거기를 기준으로 A가 뭘 수정했는지, B가 뭘 수정했는지 비교(3-Way Merge)하여 충돌을 해결할 수 있다.

#### ② 위상 정렬 (Topological Sort)
* **어디에 쓰이나?**: `git log` (히스토리 조회)
* **왜 필요한가?**: 혼자 일할 때는 커밋이 1자(Linear)로 쌓이지만, 여러 명이 브랜치를 파서 병합하면 커밋 순서가 꼬이게 된다. 위상 정렬은 "자식 커밋은 반드시 부모 커밋보다 먼저 보여야 한다"는 인과 관계 규칙을 지키면서, 복잡하게 얽힌 2차원 그래프를 1차원(한 줄) 텍스트로 예쁘게 정렬하여 터미널에 출력해 주는 역할을 한다.

#### ③ 깊이 우선 탐색(DFS) / 너비 우선 탐색(BFS)
* **어디에 쓰이나?**: `git log --graph`, `git rev-list`, `git bisect` 등
* **왜 필요한가?**: 현재 커밋(HEAD)에서 시작하여 부모 포인터를 타고 과거로 거슬러 올라가며 조상들을 모두 수집해야 할 때 사용된다.
  * 예를 들어 브랜치가 갈라진 모양을 터미널에 아스키아트(`* | \`)로 그려줄 때(DFS), 혹은 특정 커밋부터 다른 커밋까지의 최단 경로가 몇 단계인지 계산할 때(BFS) 가장 기본이 되는 순회 알고리즘이다.

### 💡 요약: 왜 알고리즘 공부와 연결되는가?
단순히 "Git 명령어를 친다"가 아니라, **"내가 명령어를 칠 때마다 메모리(혹은 디스크) 상에서 노드가 추가되고, 화살표 방향이 바뀌고, 그래프 탐색이 일어난다"**는 것을 머릿속에 그릴 수 있게 된다.
* `git log`를 치면 내부적으로 위상 정렬(Topological Sort) 또는 **깊이 우선 탐색(DFS)**이 돌아서 그래프를 위에서 아래로 출력해 준다.
* `git merge`를 치면 내부적으로 **최소 공통 조상(LCA)**을 찾는 탐색 알고리즘이 돌아간다.

---

## 💡 심층 분석: Real Git vs Mini Git

이번 과제의 설계 의도와 실제 Git의 구조적 차이를 관통하는 심층 분석이다. 

### 1. 왜 딱 이 기능들만 구현하는가?
이 과제의 목적은 "Git 클론 코딩"이 아니라 **"자료구조와 알고리즘의 실전 응용"**이기 때문이다.
저장소, 커밋, 브랜치는 **DAG(단방향 비순환 그래프)**라는 뼈대를 만들기 위한 최소한의 재료이다. 이 뼈대만 만들어지면, 그 위에서 가장 중요한 세 가지 알고리즘 훈련을 즉시 해볼 수 있다.
* **정렬 (Sorting)**: 병합 정렬(Merge Sort)을 직접 구현해 보는 훈련 (`LOG --sort-by`)
* **탐색 (Graph Traversal)**: DFS, BFS, 최단 경로, 위상 정렬 등을 실습하는 훈련 (`PATH`, `ANCESTORS`, `LOG`)
* **검색 (Search)**: O(1)의 속도를 내는 역색인(Inverted Index) 해시 테이블 구조 훈련 (`SEARCH`)

즉, 파일 시스템 복사나 복잡한 예외 처리 같은 '단순 노가다 코딩'은 싹 걷어내고, 오직 **컴퓨터 공학의 핵심(알고리즘)에만 집중할 수 있도록 알짜배기만 남겨둔 것**이다.

### 2. 실제 Git에는 어떤 기능이 더 있고, 구현하기 어려운가?
실제 Git을 바닥부터 똑같이 구현하려면 압도적으로 고난도의 기능들이 숨어 있다. 이 과제에서 생략된 진짜 Git의 복잡한 기능들은 다음과 같다.
* **파일 압축 및 스냅샷 (Blob / Tree 객체)**: 실제 Git은 폴더 안의 모든 파일 내용을 읽어서 압축(Zlib)하고, 파일 단위로 해시값을 뜬다. 이를 관리하는 기능은 디스크 I/O와 이진(Binary) 데이터 처리가 들어가서 난이도가 급상승한다.
* **Staging Area (인덱스 파일 관리)**: 흔히 쓰는 `git add` 기능이다. 커밋하기 전의 대기열 상태를 관리하는 `.git/index`라는 이진 포맷을 설계하고 파싱해야 해서 굉장히 까다롭다.
* **네트워크 통신 (Push / Pull)**: 원격 저장소 서버(GitHub)와 통신하기 위한 프로토콜과 패킷 통신 구현이다.
* **델타 압축 (Packfile)**: 10년 된 프로젝트의 용량이 폭발하지 않는 이유이다. 변경된 파일 전체를 저장하는 게 아니라, '이전 파일과 달라진 글자(Delta)'만 계산해서 압축 저장하는 고도의 최적화 알고리즘이 들어 있다.

### 3. 과제에서 구현한 명령어와 실제 Git의 차이점
명령어 문법은 거의 똑같지만 내부 작동 방식과 디테일, 출력 형태는 완전히 다르다.

| 비교 항목 | Mini Git (현재 과제) | Real Git (실제) |
| :--- | :--- | :--- |
| **해시(Hash) 생성 방식** | 무작위 난수 생성 (예: `6781a0`) | 내용 전체 기반 `SHA-1` 암호학적 해시 생성 |
| **해시(Hash) 문자열 길이** | 짧은 6자리 문자열 출력 | 40자리의 꽉 찬 긴 해시 문자열 출력 |
| **데이터 영구 저장 공간** | RAM (프로그램 끄면 즉시 휘발됨) | 하드디스크 (`.git/objects`에 영구 저장) |
| **`git log` 정렬 방향** | 과거 → 현재 (가장 오래된 커밋이 위) | 현재 → 과거 (가장 최신 커밋이 위) |
| **변경 통계 (Diff Stats)** | 진짜 파일이 없으므로 파일 통계 미제공 | `2 files changed...` 등 상세 변경 내역 제공 |
| **터미널 출력 스타일** | 텍스트 단색 출력, 이름표만 심플하게 표기 | 이메일 표기, 다채로운 터미널 색상(Color) 지원 |

### 4. 실제 Git은 왜 하필 SHA-1을 썼을까? (그리고 세대교체)
Git은 리눅스의 창시자 리누스 토발즈가 2005년에 2주 만에 개발한 프로그램이다. 당시 해시 알고리즘의 상황과 선택의 이유는 다음과 같다.
* **MD5**: 속도는 가장 빨랐지만 이미 해커들에게 뚫려 보안 결함이 심각한 상태였다.
* **SHA-256**: 극도로 안전하지만 수학 연산이 너무 무겁고 느려서 거대한 리눅스 커널 소스 코드를 해싱하기에 부적합했다.
* **SHA-1 (최종 선택)**: 속도도 매우 빠르면서, 우연히 똑같은 해시값이 나올 확률(충돌 확률)이 극도로 낮았다. 코드가 생명인 Git 입장에서는 **"스피드와 무결성(안전함)"을 모두 챙길 수 있는 가장 완벽한 밸런스**였다.

**SHA-1의 함락과 SHA-256으로의 진화**
2005년에는 안전했지만, 2017년에 구글(Google) 연구팀이 수많은 슈퍼컴퓨터를 동원해 '서로 다른 파일인데 똑같은 SHA-1 해시값이 튀어나오게 만드는 실험(SHAttered 공격)'에 성공하면서 SHA-1의 방패가 마침내 뚫렸다. 
이에 따라 현재 실제 Git은 SHA-1을 버리고, 훨씬 더 강력하고 거대한 **`SHA-256`**으로 갈아타는 초대형 마이그레이션을 몇 년째 진행 중이다. (최신 버전의 Git에서는 `git init --object-format=sha256` 명령어로 64자리의 새로운 해시 포맷을 사용할 수 있다.)

---

## 에필로그: 이전 단계 (Mini-Redis 프로젝트)와의 연결 고리

이 프로젝트(`mini-git-py`)는 이전 프로젝트인 **Mini-Redis (`mini-redis-py`)** 과의 도메인 차이점과 아키텍처적 연결 고리를 분석한다. 이 두 과제는 **"소프트웨어 엔지니어링의 근본을 바닥부터 조립한다"**는 철학에서 완벽하게 이어지는 프로젝트이다.

### 1) 어떤 느낌으로 다른가? (차이점)
가장 큰 차이는 **해결하고자 하는 문제(도메인)와 그에 필요한 핵심 자료구조**이다.
* **Mini Redis (공간과 속도의 싸움)**
  * **목표**: "한정된 메모리 공간에서 데이터를 얼마나 빠르고 효율적으로 저장하고, 쓸모없는 것을 버릴 것인가?"
  * **핵심 자료구조**: 해시맵(Hash Map), 이중 연결 리스트, 최소 힙(Min-Heap), 동적 배열(Dynamic Array)
  * **특징**: 파이썬의 기본 기능(`dict`, `list`)을 강제로 제한하고, 해시 충돌, LRU(캐시 축출), TTL(시간 만료) 등 최적화된 **'로우레벨(Low-level) 메모리 튜닝'**에 철저하게 집착하는 하드코어한 훈련이다.
* **Mini Git (관계 추적과 탐색 알고리즘)**
  * **목표**: "데이터들이 시간 흐름에 따라 얽히고설킨 복잡한 관계를 어떻게 추적하고 병합할 것인가?"
  * **핵심 자료구조**: 방향성 비순환 그래프(DAG), 위상 정렬, 최단 경로 탐색(BFS/DFS), 역색인(Inverted Index)
  * **특징**: 단순한 단일 데이터 저장을 넘어, 커밋(Commit)과 브랜치(Branch)라는 **점과 선(Graph)**의 관계망을 해석하는 **'하이레벨(High-level) 알고리즘 탐색'**에 집중한다.

### 2) 어떤 느낌에서 이어지는가? (연결점)
두 과제는 자료구조의 원리를 딛고 알고리즘으로 도약하는 형태로 강력하게 결속되어 있다.
* **자료구조의 원리(Redis)를 딛고 알고리즘(Git)으로 도약**
  * `Mini Git` 과제에서는 수많은 커밋을 빠르게 검색하기 위해 파이썬 내장 `dict`를 숨 쉬듯이 활용하게 된다. 그 `dict`가 내부적으로 어떻게 충돌을 방어하고 O(1)의 탐색 속도를 내는지 그 엔진을 밑바닥부터 깎아서 만든 것이 바로 앞선 `Mini Redis` 프로젝트이다. 즉, **Redis 프로젝트에서 뼈 빠지게 직접 깎은 '엔진(자료구조)'** 위에서 **Git 프로젝트의 '자동차(탐색 알고리즘)'**를 운전하는 셈이다.
* **트리(Tree)에서 그래프(Graph)로의 확장**
  * Redis에서 `MinHeap`과 `BST`를 만들며 부모-자식 노드의 개념(Tree)을 익혔다. Git의 커밋 히스토리는 이 트리가 더 복잡하게 얽힌 비순환 방향 그래프(DAG)이다. 트리 순회를 마스터했기 때문에 위상 정렬과 경로 탐색도 원리적으로 쉽게 접근할 수 있다.
* **REPL 기반의 상용 서버 아키텍처 통일**
  * 두 프로젝트 모두 무한 루프 기반의 REPL 구조를 가진다. 입력을 파싱하고 로직을 평가하는 이 패턴은 Node.js의 이벤트 루프나 실제 Redis C 서버가 동작하는 핵심 메커니즘과 동일하다. 계속해서 응답을 대기하는 살아 숨 쉬는 서버 애플리케이션을 설계했다는 점에서 궤를 같이한다.

### 💡 풀스택(Full-Stack) 관점에서의 한 줄 요약
결론적으로 `Mini Redis`가 한정된 자원 속에서 어떻게든 살아남는 **피지컬(기초 체력)** 훈련이었다면, `Mini Git`은 그 체력을 바탕으로 미로 속을 빠르고 정확하게 찾아가는 **뇌지컬(문제 해결 탐색)** 훈련이다. 
Redis에서 **찰흙(메모리 배열)**을 빚고 **벽돌(연결 리스트, 해시맵)**을 구워내는 훈련을 끝냈으니, Git에서는 그 벽돌들을 가지고 **거대한 성벽(그래프)**을 쌓고 **길을 내는(알고리즘)** 훈련으로 넘어가는 완벽한 빌드업 흐름을 갖는다.
