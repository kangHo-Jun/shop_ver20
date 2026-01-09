"""
간단한 Google OAuth 인증 스크립트
브라우저가 자동으로 열리지 않는 경우 사용
"""

import pickle
import webbrowser
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'google_oauth_credentials.json'
TOKEN_FILE = 'google_token.pickle'

def main():
    print("=" * 70)
    print("Google OAuth 간단 인증")
    print("=" * 70)
    print()

    creds = None

    # 기존 토큰 확인
    if Path(TOKEN_FILE).exists():
        print(f"[INFO] 기존 토큰 발견: {TOKEN_FILE}")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[INFO] 토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print(f"[INFO] 새로운 인증 시작...")
            print(f"[INFO] 자격증명 파일: {CREDENTIALS_FILE}")
            print()

            if not Path(CREDENTIALS_FILE).exists():
                print(f"[ERROR] {CREDENTIALS_FILE} 파일을 찾을 수 없습니다!")
                return False

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)

            print("[WAIT] 브라우저를 열고 있습니다...")
            print()
            print("브라우저가 자동으로 열리지 않으면:")
            print("1. 아래 URL을 복사하세요")
            print("2. 브라우저에 붙여넣기하세요")
            print("3. Google 계정으로 로그인하세요")
            print("4. 권한을 허용하세요")
            print()

            try:
                # 포트 0으로 설정하면 자동으로 사용 가능한 포트 찾음
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,  # 브라우저 자동 열기 시도
                    success_message='인증이 완료되었습니다! 이 창을 닫아도 됩니다.'
                )
            except Exception as e:
                print(f"[ERROR] 인증 중 오류: {e}")
                print()
                print("[TIP] 수동으로 브라우저를 열어 인증하세요")
                return False

        # 토큰 저장
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print()
        print(f"[OK] 토큰이 저장되었습니다: {TOKEN_FILE}")
    else:
        print("[OK] 유효한 토큰이 이미 존재합니다!")

    print()
    print("=" * 70)
    print("인증 완료!")
    print("=" * 70)
    print()
    print("다음 단계:")
    print("  python v10_auto_server.py")
    print()
    return True


if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
