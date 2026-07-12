import urllib.request
import hashlib
import os

def verify_shattered():
    print("=== 구글 SHAttered 충돌 증명 실험 ===\n")
    
    url1 = "https://shattered.io/static/shattered-1.pdf"
    url2 = "https://shattered.io/static/shattered-2.pdf"
    file1 = "shattered-1.pdf"
    file2 = "shattered-2.pdf"

    # 1. 파일 다운로드
    print("1. 구글 연구소 서버에서 2개의 PDF 파일을 다운로드합니다...")
    
    # 403 Forbidden 우회를 위해 브라우저인 척(User-Agent) 속임
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    if not os.path.exists(file1):
        req1 = urllib.request.Request(url1, headers=headers)
        with urllib.request.urlopen(req1) as response, open(file1, 'wb') as out_file:
            out_file.write(response.read())
            
    if not os.path.exists(file2):
        req2 = urllib.request.Request(url2, headers=headers)
        with urllib.request.urlopen(req2) as response, open(file2, 'wb') as out_file:
            out_file.write(response.read())
            
    print("다운로드 완료!\n")

    # 2. 파일 읽기 (바이너리 모드)
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        pdf1_data = f1.read()
        pdf2_data = f2.read()

    # 3. 해시 계산 및 비교
    print("2. 파이썬 분쇄기(SHA-1)에 넣고 돌리는 중...")
    hash1 = hashlib.sha1(pdf1_data).hexdigest()
    hash2 = hashlib.sha1(pdf2_data).hexdigest()

    print(f"\n[PDF 1] 파일 크기: {len(pdf1_data):,} bytes")
    print(f" -> SHA-1 해시 결과: {hash1}")

    print(f"\n[PDF 2] 파일 크기: {len(pdf2_data):,} bytes")
    print(f" -> SHA-1 해시 결과: {hash2}")

    # 4. 결론 도출
    print("\n================ 결과 ================")
    if pdf1_data != pdf2_data:
        print("✔️ 확인 1: 두 PDF 파일의 내용은 확실하게 다릅니다. (100% 다른 파일)")
    
    if hash1 == hash2:
        print("✔️ 확인 2: 하지만 두 파일의 SHA-1 해시값은 완벽하게 똑같습니다!")
        print("\n🚨 결론: 소름 돋는 해시 충돌 현상을 두 눈으로 증명했습니다!!")

if __name__ == "__main__":
    verify_shattered()
