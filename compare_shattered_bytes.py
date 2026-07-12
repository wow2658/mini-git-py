def inspect_pdfs():
    file1 = "shattered-1.pdf"
    file2 = "shattered-2.pdf"

    try:
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            data1 = f1.read()
            data2 = f2.read()
    except FileNotFoundError:
        print("PDF 파일이 없습니다. 먼저 다운로드 스크립트를 실행해주세요.")
        return

    print(f"총 파일 크기: {len(data1):,} 바이트")
    print("-" * 50)
    
    diff_count = 0
    diff_blocks = []
    
    # 바이트 단위로 1:1 비교
    for i in range(len(data1)):
        if data1[i] != data2[i]:
            diff_count += 1
            if not diff_blocks or diff_blocks[-1]['end'] < i - 10:
                diff_blocks.append({'start': i, 'end': i})
            else:
                diff_blocks[-1]['end'] = i

    print(f"충격적인 사실: 42만 바이트 중에 단 {diff_count}개의 바이트만 다릅니다!!")
    print("-" * 50)
    print("어디가 다를까요? (해커가 조작한 부분 탐색)\n")
    
    for block in diff_blocks:
        start = block['start']
        end = block['end']
        
        # 앞뒤로 문맥을 조금 더 보여주기 위함
        show_start = max(0, start - 16)
        show_end = min(len(data1), end + 16)
        
        print(f"📌 발견 위치: {start}번 ~ {end}번 바이트 (총 {end-start+1}바이트 조작됨)")
        
        # Hex 형태로 보기 좋게 출력
        hex1 = data1[show_start:show_end].hex(" ")
        hex2 = data2[show_start:show_end].hex(" ")
        
        print(f"[PDF 1의 조각]: ... {hex1} ...")
        print(f"[PDF 2의 조각]: ... {hex2} ...")
        print()

if __name__ == "__main__":
    inspect_pdfs()
