"""
견적서 페이지 구조 확인 (서버에서 가져온 HTML 분석)
"""
import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from v10_auto_server import browser_manager

def main():
    print("=" * 70)
    print("견적서 페이지 HTML 구조 분석")
    print("=" * 70)
    print()

    try:
        # 견적서 목록 페이지로 이동
        print("[1/2] 견적서 목록 페이지 가져오는 중...")
        browser_manager.navigate(config.YOUNGRIM_ESTIMATE_URL)
        time.sleep(3)

        page_source = browser_manager.get_source()
        soup = BeautifulSoup(page_source, 'html.parser')

        # 테이블 찾기
        table = soup.find("table")
        if not table:
            print("[ERROR] 테이블을 찾을 수 없습니다")
            return False

        all_rows = table.find_all("tr")
        if len(all_rows) < 2:
            print("[ERROR] 데이터 행이 없습니다")
            return False

        print(f"[OK] 테이블에서 {len(all_rows)-1}개 데이터 행 발견")
        print()

        # 첫 3개 데이터 행 분석
        print("=" * 70)
        print("첫 3개 데이터 행 분석:")
        print("=" * 70)

        for row_idx in range(1, min(4, len(all_rows))):
            row = all_rows[row_idx]
            cols = row.find_all("td")

            print(f"\n--- 행 {row_idx} ---")
            print(f"컬럼 개수: {len(cols)}")

            # 각 컬럼 분석
            for col_idx, col in enumerate(cols):
                text = col.get_text(strip=True)
                buttons = col.find_all("button")
                links = col.find_all("a")

                if text or buttons or links:
                    print(f"\n  컬럼 {col_idx}:")
                    if text:
                        print(f"    텍스트: {text[:50]}")

                    if buttons:
                        for btn_idx, button in enumerate(buttons):
                            print(f"    버튼 {btn_idx}:")
                            print(f"      class: {button.get('class')}")
                            print(f"      text: {button.get_text(strip=True)}")
                            # 모든 속성 출력
                            for attr_name in button.attrs:
                                if attr_name not in ['class']:
                                    print(f"      {attr_name}: {button.get(attr_name)}")

                    if links:
                        for link_idx, link in enumerate(links):
                            print(f"    링크 {link_idx}:")
                            print(f"      href: {link.get('href')}")
                            print(f"      onclick: {link.get('onclick')}")
                            print(f"      text: {link.get_text(strip=True)}")

        print("\n" + "=" * 70)
        print("[완료] 분석 완료")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
