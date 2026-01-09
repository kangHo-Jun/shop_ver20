"""
이카운트 로그인 페이지 구조 확인
"""
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from bs4 import BeautifulSoup

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config

def main():
    print("=" * 70)
    print("이카운트 로그인 페이지 HTML 구조 확인")
    print("=" * 70)
    print()

    # Edge 연결
    print("[1/2] Edge 브라우저 연결 중...")
    edge_options = EdgeOptions()
    edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9333")

    try:
        driver = webdriver.Edge(options=edge_options)
        print("[OK] 연결 성공!")
        print()
    except Exception as e:
        print(f"[ERROR] 연결 실패: {e}")
        return

    # 이카운트 로그인 페이지로 이동
    print("[2/2] 이카운트 로그인 페이지로 이동...")
    driver.get(config.ECOUNT_LOGIN_URL)
    time.sleep(3)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    print("[OK] 페이지 로드 완료")
    print()

    # 입력 필드 찾기
    print("=" * 70)
    print("입력 필드 (input) 분석:")
    print("=" * 70)

    inputs = soup.find_all("input")
    for idx, input_field in enumerate(inputs[:15]):  # 처음 15개만
        input_type = input_field.get("type", "")
        input_id = input_field.get("id", "")
        input_name = input_field.get("name", "")
        input_placeholder = input_field.get("placeholder", "")
        input_class = input_field.get("class", "")

        if input_type or input_id or input_name:
            print(f"\n입력 필드 {idx+1}:")
            if input_id:
                print(f"  ID: {input_id}")
            if input_name:
                print(f"  Name: {input_name}")
            if input_type:
                print(f"  Type: {input_type}")
            if input_placeholder:
                print(f"  Placeholder: {input_placeholder}")
            if input_class:
                print(f"  Class: {input_class}")

    # 버튼 찾기
    print("\n" + "=" * 70)
    print("버튼 (button) 분석:")
    print("=" * 70)

    buttons = soup.find_all("button")
    for idx, button in enumerate(buttons[:10]):  # 처음 10개만
        button_id = button.get("id", "")
        button_type = button.get("type", "")
        button_text = button.get_text(strip=True)
        button_class = button.get("class", "")

        print(f"\n버튼 {idx+1}:")
        if button_id:
            print(f"  ID: {button_id}")
        if button_type:
            print(f"  Type: {button_type}")
        if button_text:
            print(f"  Text: {button_text}")
        if button_class:
            print(f"  Class: {button_class}")

    print("\n" + "=" * 70)
    print("[완료] 분석 완료")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
