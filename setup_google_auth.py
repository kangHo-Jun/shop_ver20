"""
Google OAuth 인증 설정 스크립트
================================
최초 1회 실행하여 Google Sheets API 토큰 생성

실행 방법:
    python setup_google_auth.py

실행 후:
    - 브라우저가 자동으로 열립니다
    - Google 계정으로 로그인
    - 권한 허용
    - google_token.pickle 파일이 생성됩니다
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lock_manager import DistributedLockManager
from config import config

def main():
    print("=" * 70)
    print("Google OAuth 인증 설정")
    print("=" * 70)
    print()

    # 1. 환경 확인
    print("[1/4] 환경 확인 중...")
    if not config.GOOGLE_CREDENTIALS_PATH.exists():
        print(f"[ERROR] OAuth 자격증명 파일을 찾을 수 없습니다:")
        print(f"   {config.GOOGLE_CREDENTIALS_PATH}")
        print()
        print("해결 방법:")
        print("1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성")
        print("2. JSON 파일을 'google_oauth_credentials.json'로 저장")
        return False

    print(f"[OK] OAuth 자격증명 파일 확인: {config.GOOGLE_CREDENTIALS_PATH.name}")
    print()

    # 2. 기존 토큰 확인
    print("[2/4] 기존 토큰 확인 중...")
    if config.GOOGLE_TOKEN_PATH.exists():
        print(f"[WARNING]  기존 토큰 파일이 존재합니다: {config.GOOGLE_TOKEN_PATH.name}")
        response = input("   기존 토큰을 삭제하고 새로 생성하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("   작업이 취소되었습니다.")
            return False

        config.GOOGLE_TOKEN_PATH.unlink()
        print("   [OK] 기존 토큰 삭제됨")
    else:
        print("[OK] 새 토큰을 생성합니다.")
    print()

    # 3. OAuth 인증 진행
    print("[3/4] Google OAuth 인증 진행 중...")
    print("[WAIT] 브라우저가 자동으로 열립니다...")
    print("   1. Google 계정으로 로그인하세요")
    print("   2. 권한 요청을 확인하고 '허용'을 클릭하세요")
    print("      - Google Sheets 읽기/쓰기 권한")
    print("      - Google Drive 읽기 권한")
    print("   3. 'The authentication flow has completed' 메시지가 나오면 브라우저를 닫으세요")
    print()

    try:
        lock_mgr = DistributedLockManager()

        # connect() 메서드가 내부적으로 OAuth 인증 처리
        success = lock_mgr.connect()

        if not success:
            print("[ERROR] 인증 실패")
            return False

        print()
        print("[OK] OAuth 인증 완료!")
        print(f"[OK] 토큰 파일 생성: {config.GOOGLE_TOKEN_PATH}")
        print()

    except KeyboardInterrupt:
        print("\n[WARNING]  사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        print(f"\n[ERROR] 인증 중 오류 발생: {e}")
        return False

    # 4. 연결 테스트
    print("[4/4] 연결 테스트 중...")
    try:
        # Google Sheets 정보 확인
        print(f"   Spreadsheet ID: {config.GS_SPREADSHEET_ID}")
        print(f"   Lock Sheet Name: {config.LOCK_SHEET_NAME}")

        # 락 시트 확인
        if lock_mgr.lock_worksheet:
            print(f"[OK] Google Sheets 연결 성공!")
            print(f"   Lock sheet: '{lock_mgr.lock_worksheet.title}'")

            # 현재 락 개수 확인
            all_locks = lock_mgr.get_all_locks()
            print(f"   현재 락 레코드: {len(all_locks)}개")
        else:
            print("[WARNING]  Lock worksheet를 찾을 수 없습니다.")

    except Exception as e:
        print(f"[WARNING]  연결 테스트 중 경고: {e}")

    print()
    print("=" * 70)
    print("설정 완료!")
    print("=" * 70)
    print()
    print("다음 단계:")
    print("1. 이제 V10 서버를 실행할 수 있습니다:")
    print("   python v10_auto_server.py")
    print()
    print("2. 또는 배치 파일로 실행:")
    print("   run_v10_server.bat")
    print()
    print("보안 주의사항:")
    print("- google_token.pickle 파일을 절대 공유하지 마세요")
    print("- 이 파일은 .gitignore에 추가되어 있습니다")
    print()

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
