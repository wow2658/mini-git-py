import struct
from typing import Optional

def merge_sort(arr, key=lambda x: x):
    """
    병합 정렬 알고리즘 (Stable Sort).
    시간 복잡도: 평균/최악 O(N log N)
    """
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(arr, key=lambda x: x):
    """
    퀵 정렬 알고리즘.
    시간 복잡도: 평균 O(N log N), 최악 O(N^2)
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if key(x) < key(pivot)]
    middle = [x for x in arr if key(x) == key(pivot)]
    right = [x for x in arr if key(x) > key(pivot)]
    return quick_sort(left, key) + middle + quick_sort(right, key)


def bubble_sort(arr, key=lambda x: x):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if key(arr[j]) > key(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr, key=lambda x: x):
    for i in range(1, len(arr)):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and key(arr[j]) > key(key_item):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item
    return arr


def selection_sort(arr, key=lambda x: x):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if key(arr[j]) < key(arr[min_idx]):
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def heap_sort(arr, key=lambda x: x):
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and key(arr[l]) > key(arr[largest]):
            largest = l
        if r < n and key(arr[r]) > key(arr[largest]):
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
            
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr


def counting_sort_for_radix(arr, exp, key):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    for i in range(n):
        index = (key(arr[i]) // exp) % 10
        count[index] += 1
        
    for i in range(1, 10):
        count[i] += count[i - 1]
        
    i = n - 1
    while i >= 0:
        index = (key(arr[i]) // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1
        
    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr, key=lambda x: x):
    if not arr: return arr
    max_val = max(key(x) for x in arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort_for_radix(arr, exp, key)
        exp *= 10
    return arr


def python_sort(arr, key=lambda x: x):
    arr.sort(key=key)
    return arr


def get_ancestors(repo, start_hash: str) -> set[str]:
    """
    해당 커밋의 모든 조상 커밋(부모 및 상위 조상)의 해시 집합을 반환합니다. (BFS 사용)
    자기 자신은 조상에 포함되지 않으며, 부모 노드부터 상위로 탐색합니다.
    """
    if start_hash not in repo.commits:
        return set()
    
    visited = set()
    queue = list(repo.commits[start_hash].parents)
    
    while queue:
        current = queue.pop(0)
        if current not in visited:
            visited.add(current)
            if current in repo.commits:
                commit = repo.commits[current]
                for parent in commit.parents:
                    queue.append(parent)
                
    return visited


def build_children_map(repo) -> dict[str, list[str]]:
    """
    커밋 객체의 parents(부모) 목록을 역으로 뒤집어,
    부모 커밋 해시 -> 자식 커밋 해시 목록 매핑(순방향 간선)을 생성합니다.
    LOG(위상 정렬) 및 PATH(무방향 최단 경로) 탐색에서 공통으로 재사용됩니다.
    """
    children_map = {c: [] for c in repo.commits}
    for c_hash, c_obj in repo.commits.items():
        for p in c_obj.parents:
            if p in children_map:
                children_map[p].append(c_hash)
            else:
                children_map[p] = [c_hash]
    return children_map


def shortest_path(repo, hash1: str, hash2: str) -> Optional[list[str]]:
    """
    두 커밋 간의 최단 경로를 반환합니다. 간선을 무방향으로 취급합니다.
    경로가 여러 개일 경우 사전순(lexicographical)으로 가장 작은 경로를 선택합니다.
    """
    if hash1 not in repo.commits or hash2 not in repo.commits:
        return None
    
    if hash1 == hash2:
        return [hash1]
        
    # 공통 함수를 재사용하여 자식 방향 순방향 간선 맵 획득
    children_map = build_children_map(repo)
                
    # BFS 탐색 (모든 최단 경로 찾기)
    distances = {hash1: 0}
    queue = [[hash1]]
    valid_paths = []
    min_length = float('inf')
    
    while queue:
        path = queue.pop(0)
        current = path[-1]
        
        if current == hash2:
            if len(path) < min_length:
                min_length = len(path)
                valid_paths = [path]
            elif len(path) == min_length:
                valid_paths.append(path)
            continue
            
        if len(path) >= min_length:
            continue
            
        # 이웃: 부모 커밋 + 자식 커밋
        neighbors = repo.commits[current].parents + children_map.get(current, [])
        for n in neighbors:
            if n not in distances or distances[n] >= len(path):
                distances[n] = len(path)
                queue.append(path + [n])
                
    if not valid_paths:
        return None
        
    def path_to_str(p):
        return "->".join(p)
        
    # 사전순으로 정렬 후 첫 번째(가장 작은) 경로 반환
    valid_paths = merge_sort(valid_paths, key=path_to_str)
    return valid_paths[0]


def topological_sort_commits(repo) -> list[str]:
    """
    커밋들을 위상 정렬하여 반환합니다.
    부모 커밋이 자식 커밋보다 항상 먼저 출력되도록 정렬합니다.
    """
    in_degree = {c: len(repo.commits[c].parents) for c in repo.commits}
    # 공통 함수를 재사용하여 자식 방향 순방향 간선 맵 획득
    children_map = build_children_map(repo)
                
    # 진입 차수가 0인 커밋(부모가 없는 최초의 커밋들)부터 시작
    queue = [c for c in repo.commits if in_degree[c] == 0]
    result = []
    
    while queue:
        # 큐 내에서 날짜순으로 한 번 더 정렬하여 출력 결과를 예측 가능하게 함
        queue = merge_sort(queue, key=lambda x: repo.commits[x].timestamp)
        current = queue.pop(0)
        result.append(current)
        
        for child in children_map.get(current, []):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)
                
    return result


def lcs_diff(lines1: list[str], lines2: list[str]) -> list[str]:
    """
    기본 교육용 LCS Diff Algorithm (DP 기반).
    시간 복잡도: O(N*M)
    """
    m, n = len(lines1), len(lines2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if lines1[i-1] == lines2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                
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
    return diff_res


def myers_diff(a: list[str], b: list[str]) -> list[str]:
    """
    Myers Diff Algorithm.
    시간 복잡도: O(ND)
    """
    n = len(a)
    m = len(b)
    max_d = n + m
    if max_d == 0:
        return []
        
    v = [0] * (2 * max_d + 1)
    trace = []
    
    for d in range(max_d + 1):
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            idx = max_d + k
            
            if k == -d or (k != d and v[idx - 1] < v[idx + 1]):
                x = v[idx + 1]
            else:
                x = v[idx - 1] + 1
                
            y = x - k
            
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
                
            v[idx] = x
            
            if x >= n and y >= m:
                return _backtrack_myers(trace, a, b, max_d)
                
    return []

def _backtrack_myers(trace, a, b, max_d) -> list[str]:
    x, y = len(a), len(b)
    diff_res = []
    
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        idx = max_d + k
        
        if k == -d or (k != d and v[idx - 1] < v[idx + 1]):
            prev_k = k + 1
        else:
            prev_k = k - 1
            
        # trace[d]는 d 단계 시작 직전, 즉 d-1 단계까지의 경로를 담는다.
        prev_x = v[max_d + prev_k] if d > 0 else 0
        prev_y = prev_x - prev_k
        
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            diff_res.append("  " + a[x].rstrip())
            
        if d > 0:
            if x == prev_x:
                y -= 1
                diff_res.append("+ " + b[y].rstrip())
            else:
                x -= 1
                diff_res.append("- " + a[x].rstrip())
                
    diff_res.reverse()
    return diff_res

# ==========================================
# 커스텀 해시 (Custom SHA-256) 구현
# ==========================================
def right_rotate(n, b):
    return ((n >> b) | (n << (32 - b))) & 0xffffffff

def _ch(e, f, g):
    return (e & f) ^ (~e & g)

def _maj(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)

def _sigma0(a):
    return right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)

def _sigma1(e):
    return right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)

def _gamma0(w):
    return right_rotate(w, 7) ^ right_rotate(w, 18) ^ (w >> 3)

def _gamma1(w):
    return right_rotate(w, 17) ^ right_rotate(w, 19) ^ (w >> 10)

def my_sha256(message: bytes) -> str:
    """
    입력된 메시지를 SHA-256 수학적 알고리즘을 거쳐 
    고정된 64자리 16진수 해시로 변환합니다. (외부 라이브러리 미사용)
    """
    import struct
    
    # 1. 초기 해시값 (소수들의 제곱근 소수점 이하 비트)
    H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # 2. 64개의 상수 K (소수들의 세제곱근 소수점 이하 비트)
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    # 3. 패딩(Padding) 작업: 데이터를 64바이트(512비트) 블록 단위로 맞춤
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'
    message += b'\x00' * ((56 - (original_byte_len + 1) % 64) % 64)
    message += struct.pack('>Q', original_bit_len)

    # 4. 64바이트 블록 단위로 쪼개서 64라운드 연산
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 64
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
            
        # 메시지 확장 연산 (64라운드)
        for j in range(16, 64):
            s0 = _gamma0(w[j-15])
            s1 = _gamma1(w[j-2])
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffff
            
        a, b, c, d, e, f, g, h = H
        
        # 64라운드 메인 로직
        for j in range(64):
            S1 = _sigma1(e)
            ch_val = _ch(e, f, g)
            temp1 = (h + S1 + ch_val + K[j] + w[j]) & 0xffffffff
            S0 = _sigma0(a)
            maj_val = _maj(a, b, c)
            temp2 = (S0 + maj_val) & 0xffffffff
            
            h = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff
            
        # 블록 단위 결과 더하기
        H[0] = (H[0] + a) & 0xffffffff
        H[1] = (H[1] + b) & 0xffffffff
        H[2] = (H[2] + c) & 0xffffffff
        H[3] = (H[3] + d) & 0xffffffff
        H[4] = (H[4] + e) & 0xffffffff
        H[5] = (H[5] + f) & 0xffffffff
        H[6] = (H[6] + g) & 0xffffffff
        H[7] = (H[7] + h) & 0xffffffff

    # 5. 64자리 16진수 문자열로 반환
    return '%08x%08x%08x%08x%08x%08x%08x%08x' % tuple(H)
