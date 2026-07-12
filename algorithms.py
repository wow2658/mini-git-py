import struct

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
    해당 커밋에서 도달 가능한 모든 조상 커밋의 해시를 반환합니다. (BFS 사용)
    """
    if start_hash not in repo.commits:
        return set()
    
    visited = set()
    queue = [start_hash]
    
    while queue:
        current = queue.pop(0)
        if current not in visited:
            visited.add(current)
            commit = repo.commits[current]
            for parent in commit.parents:
                queue.append(parent)
                
    return visited


def shortest_path(repo, hash1: str, hash2: str) -> list[str] | None:
    """
    두 커밋 간의 최단 경로를 반환합니다. 간선을 무방향으로 취급합니다.
    경로가 여러 개일 경우 사전순(lexicographical)으로 가장 작은 경로를 선택합니다.
    """
    if hash1 not in repo.commits or hash2 not in repo.commits:
        return None
    
    if hash1 == hash2:
        return [hash1]
        
    # 자식 방향 간선을 위한 매핑 구성
    children_map = {c: [] for c in repo.commits}
    for c_hash, c_obj in repo.commits.items():
        for p in c_obj.parents:
            if p in children_map:
                children_map[p].append(c_hash)
            else:
                children_map[p] = [c_hash]
                
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
    children_map = {c: [] for c in repo.commits}
    
    for c_hash, c_obj in repo.commits.items():
        for p in c_obj.parents:
            if p in children_map:
                children_map[p].append(c_hash)
            else:
                children_map[p] = [c_hash]
                
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
            
        prev_x = trace[d - 1][max_d + prev_k] if d > 0 else 0
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
# 커스텀 해시 (Custom SHA-1) 구현
# ==========================================
def left_rotate(n, b):
    # 32비트 비트 시프트(순환 이동) 연산
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def my_sha1(message: bytes) -> str:
    """
    입력된 메시지를 SHA-1 수학적 알고리즘을 거쳐 
    고정된 40자리 16진수 해시로 변환합니다.
    """
    # 1. 매직 넘버 초기화 (SHA-1 스펙)
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    # 2. 패딩(Padding) 작업: 데이터를 64바이트(512비트) 블록으로 맞춤
    import struct
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'
    message += b'\x00' * ((56 - (original_byte_len + 1) % 64) % 64)
    message += struct.pack('>Q', original_bit_len)

    # 3. 64바이트 블록 단위로 쪼개서 복잡한 수학 연산 80회 반복
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 80
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
        
        # 메시지 확장 연산 (XOR 연산)
        for j in range(16, 80):
            w[j] = left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)
            
        a, b, c, d, e = h0, h1, h2, h3, h4
        
        # 80라운드의 비트 마스킹 및 논리 연산
        for j in range(80):
            if 0 <= j <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= j <= 79:
                f = b ^ c ^ d
                k = 0xCA62C1D6
                
            temp = (left_rotate(a, 5) + f + e + k + w[j]) & 0xffffffff
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
            
        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff

    # 4. 결과값 결합
    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)
