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
