from models import Commit, Repository
import random
import time

def hack_mini_git():
    print("=== Mini Git 7자리 해시 충돌 해킹(장난질) 시작 ===")
    print("우리의 Mini Git은 터미널 가독성을 위해 해시의 '앞 7자리'만 사용합니다.")
    print("7자리 16진수의 경우의 수는 16^7 = 약 2억 6천만 개입니다.")
    print("하지만 '생일 문제(Birthday Paradox)' 수학 원리에 의해, 약 16,000번만 무작위 커밋을 생성하면 높은 확률로 충돌을 찾을 수 있습니다!\n")
    
    print("1. 해시가 완전히 똑같이 떨어지는 '착한 커밋'과 '악성 커밋' 짝꿍 찾는 중... (슈퍼컴퓨터 불필요, 1초면 컷!)")
    start_time = time.time()
    
    seen_hashes = {}
    good_commit = None
    evil_commit = None
    attempts = 0
    
    while True:
        attempts += 1
        # 무작위 데이터를 섞어 커밋 메시지 생성
        random_msg = f"Random Data {random.randint(1, 10000000)}"
        temp_commit = Commit(random_msg, "Hacker", [])
        
        # 만약 방금 만든 커밋의 7자리 해시가 이전에 만든 적 있는 해시라면? (충돌 발생!)
        if temp_commit.hash in seen_hashes:
            good_commit = seen_hashes[temp_commit.hash]
            good_commit.message = "Good Commit: 정상적인 보안 패치 업데이트입니다."
            good_commit.author = "Alice"
            
            evil_commit = temp_commit
            evil_commit.message = "Evil Commit: [해킹 성공] 백도어를 몰래 설치했습니다!"
            evil_commit.author = "Hacker"
            break
        else:
            seen_hashes[temp_commit.hash] = temp_commit
            
    elapsed = time.time() - start_time
    print(f" -> 성공! 불과 {attempts:,}번의 시도만에 충돌을 발견했습니다. (소요 시간: {elapsed:.2f}초)\n")
    
    print("=== 2. 착한 커밋과 악성 커밋의 정보 비교 ===")
    print(f"[착한 커밋] 작성자: {good_commit.author} / 메시지: {good_commit.message}")
    print(f"            => 해시값: {good_commit.hash}")
    print(f"[악성 커밋] 작성자: {evil_commit.author} / 메시지: {evil_commit.message}")
    print(f"            => 해시값: {evil_commit.hash}")
    
    print("\n=== 3. Mini Git 저장소 테러 시뮬레이션 ===")
    repo = Repository()
    
    print("Alice가 착한 커밋을 저장소에 올립니다 (git commit).")
    repo.commits[good_commit.hash] = good_commit
    
    print("Hacker가 악성 커밋을 똑같은 저장소에 올립니다 (git push).")
    # 딕셔너리 구조상 키(해시)가 같으면 아무런 경고 없이 이전 데이터가 덮어씌워짐!!
    repo.commits[evil_commit.hash] = evil_commit
    
    print("\n[현재 저장소에 저장된 커밋 조회 (git log)]")
    # 저장소에는 분명히 커밋이 1개만 있음 (해시가 겹쳐서 덮어씌워졌으므로)
    for h, c in repo.commits.items():
        print(c)
        
    print("\n🚨 대형 사고 발생: 앨리스의 정상 코드는 흔적도 없이 사라지고, 해커의 악성 코드가 그 자리를 완벽하게 차지했습니다!")

if __name__ == "__main__":
    hack_mini_git()
