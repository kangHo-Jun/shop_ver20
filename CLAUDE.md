# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Youngrim Order Automation System** that automatically downloads order documents from Youngrim OMS and uploads them to Ecount ERP. The system has two major versions:

- **V8.1**: Single-machine automation with JSON-based local history
- **V10**: Multi-machine automation with Google Sheets-based distributed lock system

The system is designed for Windows environments and uses browser automation (Selenium/Playwright) to interact with web interfaces.

## Development Policy

- **Auto-commit**: ON. Every successful task completion must be followed by a git commit with a descriptive message.

## Running the System

### V8 (Single Machine)
```bash
# Run V8 server
run_v8_server.bat

# Web dashboard
http://localhost:5080
```

### V10 (Multi-Machine with Distributed Lock)
```bash
# First time setup - Edge browser in debug mode
start_edge_debug.bat

# Run V10 server
run_v10_server.bat

# Web dashboard
http://localhost:5080
```

### Initial Setup
```bash
# One-time setup: create venv and install dependencies
setup_env.bat

# Manual setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Configuration
- Copy `.env.example` to `.env` for V8
- Copy `.env.v10.example` to `.env` for V10
- Configure Google OAuth credentials in `google_oauth_credentials.json`

## Core Architecture

### Data Flow
```
Youngrim OMS (door.yl.co.kr)
    ↓ [Selenium WebDriver]
Download HTML/MHTML orders
    ↓ [local_file_processor.py]
Parse & generate item codes
    ↓ [Write to Google Sheets]
ERP sheet with formatted data
    ↓ [erp_upload_automation_v2.py]
Upload to Ecount ERP (login.ecount.com)
```

### V10 Distributed Lock System
```
PC-A, PC-B, PC-C (multiple V10 servers)
    ↓
Google Sheets "processing_lock" sheet
    ↓
Lock acquisition (atomic, with timeout)
    ↓
Process order (only one PC processes each order)
    ↓
Update lock status: processing → completed
```

### Key Components

**Main Servers:**
- `v8_auto_server.py` - V8 Flask server (single machine)
- `v10_auto_server.py` - V10 Flask server (multi-machine with distributed lock)

**Core Logic:**
- `local_file_processor.py` - Parses HTML/MHTML, extracts order data, generates item codes
- `erp_upload_automation_v2.py` - Playwright-based ERP upload automation (reads from Google Sheets, uploads to Ecount)
- `lock_manager.py` - V10 distributed lock manager using Google Sheets

**Foundation:**
- `config.py` - Centralized configuration loader (reads from `.env`)
- `logging_config.py` - JSON structured logging with daily rotation
- `error_handler.py` - Error tracking with severity levels and exponential backoff retry

**Browser Automation:**
- V8 uses Avast Secure Browser with Selenium
- V10 uses Edge browser in debug mode (CDP port 9333) with Selenium
- ERP upload uses Playwright (Chromium)

### Directory Structure
```
shop_ver20/
├── data/downloads/          # Downloaded orders (ledger, estimate)
├── logs/                    # JSON logs (app_YYYYMMDD.json, critical_errors.json)
│   └── uploader/           # ERP upload logs
├── google_oauth_credentials.json  # Google API credentials (NEVER commit)
├── google_token.pickle     # Google auth token cache
├── ecount_session.json     # Ecount session cache
├── v8_history.json         # V8 processing history
├── v10_history.json        # V10 processing history
└── .env                    # Environment configuration (NEVER commit)
```

## Critical Implementation Details

### Browser Automation Requirements

**V8 Browser Setup:**
- Requires Avast Secure Browser installed at: `C:\Program Files\AVAST Software\Browser\Application\AvastBrowser.exe`
- Uses Selenium with ChromeDriver version 142
- Must maintain login session on Youngrim OMS

**V10 Browser Setup:**
- Requires Microsoft Edge browser
- Must run Edge in debug mode first: `start_edge_debug.bat`
- Debug port: 9333
- Profile location: `edge_automation_profile/`
- Server connects to existing debug session (CDP protocol)

**ERP Upload Browser:**
- Uses Playwright with Chromium
- Separate from main browser automation
- Handles Ecount login and data upload

### Distributed Lock System (V10)

**Lock Record Structure (Google Sheets):**
| order_id | locked_by | locked_at | status | machine_id | notes |
|----------|-----------|-----------|---------|------------|-------|

**Lock States:**
- `processing` - Currently being processed by a machine
- `completed` - Successfully processed (will not be reprocessed)
- `failed` - Processing failed (can be retried)

**Lock Timeout:**
- Default: 30 minutes (1800 seconds)
- Prevents deadlock if a machine crashes
- Configured via `LOCK_TIMEOUT_SEC` in `.env`

**Machine Identification:**
- Format: `{hostname}_{ip_address}`
- Automatically generated on startup
- Used to identify which PC is processing each order

### Configuration Management

All configuration is centralized in `config.py` which reads from `.env`:

**Key Settings:**
- `FLASK_PORT` - Web dashboard port (default: 5080)
- `DOWNLOAD_INTERVAL_SEC` - Polling interval for new orders (default: 1800)
- `BROWSER_DEBUG_PORT` - Edge debug port for V10 (default: 9333)
- `ENABLE_DISTRIBUTED_LOCK` - Enable/disable distributed lock (V10 only)
- `LOCK_TIMEOUT_SEC` - Lock timeout in seconds (V10 only)
- `GS_SPREADSHEET_ID` - Google Sheets ID for data storage
- `ECOUNT_COMPANY_CODE`, `ECOUNT_ID`, `ECOUNT_PASSWORD` - ERP credentials

### Error Handling

The system uses structured error handling via `error_handler.py`:

**Error Severity Levels:**
- `CRITICAL` - System cannot continue, logged to `critical_errors.json`
- `HIGH` - Operation failed but system can continue
- `MEDIUM` - Recoverable error with retry
- `LOW` - Warning or informational

**Retry Mechanism:**
- Exponential backoff with configurable max retries
- `MAX_RETRIES` and `RETRY_DELAY_SEC` in config
- Applied to network operations and ERP uploads

### Google Sheets Integration

**Authentication:**
- OAuth 2.0 flow with `google_oauth_credentials.json`
- Token cached in `google_token.pickle`
- Automatic token refresh on expiry

**Sheet Structure:**
- Main data sheet: `erp` (configured via `GS_SHEET_NAME`)
- Lock sheet (V10): `processing_lock` (configured via `LOCK_SHEET_NAME`)
- Spreadsheet ID in `.env` as `GS_SPREADSHEET_ID`

**API Scopes:**
- Upload automation: `spreadsheets.readonly` (read ERP data)
- Lock manager: `spreadsheets` (read/write lock records)

## Common Development Tasks

### Testing Distributed Lock
```bash
.venv\Scripts\activate
python lock_manager.py
```

### Viewing Logs
```bash
# Main application logs (JSON format)
logs/app_YYYYMMDD.json

# Critical errors only
logs/critical_errors.json

# ERP upload logs
logs/uploader/erp_upload_*.log
```

### Debugging Browser Issues

**V10 Edge Connection:**
1. Ensure Edge is running in debug mode (port 9333)
2. Check profile location: `edge_automation_profile/`
3. Test connection: `http://localhost:9333/json/version`

**V8 Avast Browser:**
1. Verify installation path in config
2. Check ChromeDriver version compatibility
3. Ensure login session is active on Youngrim site

### Adding New Features

**When modifying order processing logic:**
1. Update `local_file_processor.py` for parsing changes
2. Ensure changes work for both ledger and estimate types
3. Test with actual downloaded HTML/MHTML files
4. Update item code generation logic if needed

**When modifying ERP upload:**
1. Changes go in `erp_upload_automation_v2.py`
2. Test with Google Sheets connection
3. Verify clipboard operations for paste functionality
4. Check Playwright selectors for Ecount UI changes

**When adding distributed lock features:**
1. Modify `lock_manager.py` for lock logic
2. Update `v10_auto_server.py` for server integration
3. Test multi-machine scenarios
4. Document lock sheet schema changes

## Important Notes

### Security

**NEVER commit these files:**
- `.env` - Contains credentials
- `google_oauth_credentials.json` - OAuth client secrets
- `google_token.pickle` - Auth tokens
- `ecount_session.json` - Session data
- `*_history.json` - May contain order data
- `data/downloads/` - Contains real order documents
- `logs/` - May contain sensitive information

All sensitive files are listed in `.gitignore`.

### Windows-Specific Code

This codebase is **Windows-only**:
- Uses Windows batch files (`.bat`) for execution
- Browser paths are Windows-specific
- File path handling uses Windows conventions
- Some browser automation relies on Windows-specific features

### Browser Session Management

**Critical:** The automation relies on browser sessions being maintained:
- V8: Avast Browser must stay logged into Youngrim OMS
- V10: Edge debug session must remain active
- Closing the browser will break automation until re-login

### Version Compatibility

**V8.1 vs V10 - Choose based on deployment:**
- **Use V8.1 when:** Single machine, no network dependency
- **Use V10 when:** Multiple machines need to share workload, central monitoring required

**Both versions share:**
- Same parsing logic (`local_file_processor.py`)
- Same ERP upload logic (`erp_upload_automation_v2.py`)
- Same configuration system (`config.py`)
- Different history files (`v8_history.json` vs `v10_history.json`)

### Korean Language Support

- HTML parsing handles EUC-KR and UTF-8 encoding
- Company name mapping includes Korean text (영림, 우딘, 예림)
- Logs may contain Korean characters
- Ensure console/editor supports UTF-8 for proper display

## Web Dashboard API

The Flask server exposes these endpoints:

**Status API:**
- `GET /api/stats` - System status, pending counts, lock manager state
- `GET /api/pending` - List of pending orders
- `GET /api/history` - Processing history

**Control API:**
- `POST /trigger_download` - Manual download trigger
- `POST /upload_ledger` - Manual ledger upload
- `POST /upload_estimate` - Manual estimate upload

Dashboard updates every 3 seconds via JavaScript fetch.

## Troubleshooting Common Issues

**"Lock manager not connected"** (V10)
- Check Google Sheets API credentials
- Verify internet connection
- Ensure `processing_lock` sheet exists
- Set `ENABLE_DISTRIBUTED_LOCK=false` to run without lock

**"Browser not found" or connection errors:**
- V8: Verify Avast Browser installation path
- V10: Ensure `start_edge_debug.bat` was run first
- Check debug port availability (9333)

**"Orders processed multiple times"** (V10)
- Distributed lock might be disabled
- Check `ENABLE_DISTRIBUTED_LOCK=true` in `.env`
- Verify Google Sheets lock sheet is accessible

**"ERP upload fails":**
- Check Ecount credentials in `.env`
- Verify Google Sheets connection
- Check clipboard functionality (pyperclip)
- Review logs in `logs/uploader/`

**"start_edge_debug.bat doesn't open when double-clicked"** (V10)
- This is a known Windows batch file behavior
- **Solution**: Run from command prompt instead:
  ```cmd
  cd C:\Users\DS-Sales0\shop_ver20
  start_edge_debug.bat
  ```
- The batch file works correctly when executed from command prompt
- Once Edge is running in debug mode (port 9333), the V10 server will connect automatically

## Lessons Learned

### 2026-01-13: Multi-Page Download Support & Edge Browser Profile Issue

**Problem**: System was only downloading from 2 pages, but Youngrim OMS has separate pages for "산업" and "임업" categories (4 pages total).

**Solution**: Modified the system to support multiple download URLs:
- Updated [config.py:15-32](config.py#L15-L32) to use URL lists instead of single URLs
- Modified [v10_auto_server.py:323-346](v10_auto_server.py#L323-L346) to iterate through multiple URLs
- Modified [v8_auto_server.py:287-310](v8_auto_server.py#L287-L310) for consistency

**Download Pages Now Supported**:
1. Ledger 산업: `http://door.yl.co.kr/oms/ledger_list.jsp?search_action=&younglim_gubun=%EC%82%B0%EC%97%85`
2. Ledger 임업: `http://door.yl.co.kr/oms/ledger_list.jsp?search_action=&younglim_gubun=%EC%9E%84%EC%97%85`
3. Estimate 산업: `http://door.yl.co.kr/oms/estimate_list.jsp?search_action=&younglim_gubun=%EC%82%B0%EC%97%85`
4. Estimate 임업: `http://door.yl.co.kr/oms/estimate_list.jsp?search_action=&younglim_gubun=%EC%9E%84%EC%97%85`

**Edge Browser Profile Issue**:
- **Problem**: User already had logged-in Edge profile at `C:\Users\DS-Sales0\AppData\Local\Microsoft\Edge\User Data\Default`, but batch file was trying to create new automation profile
- **Insight**: Using existing logged-in profile is much better than creating new profile and re-authenticating
- **Solution**: Modified [start_edge_debug.bat:47-54](start_edge_debug.bat#L47-L54) to use Default profile instead of edge_automation_profile
- **Result**: No need to re-login to Youngrim OMS, immediate automation start

**Batch File Execution Issue**:
- **Finding**: Windows batch files sometimes don't execute properly when double-clicked, but work fine from command prompt
- **Workaround**: Always run `start_edge_debug.bat` from command prompt with explicit directory change
- **Not a bug**: This is expected Windows behavior for certain batch file configurations

**Server Restart After Browser Connection**:
- **Issue**: If V10 server starts before Edge browser is running in debug mode, the downloader thread enters error state
- **Solution**: Restart V10 server after Edge is running to establish proper browser connection
- **Prevention**: Always run `start_edge_debug.bat` BEFORE running `run_v10_server.bat`

**Verification Results** (2026-01-13 15:37):
- Ledger 산업: 47 rows found
- Ledger 임업: 19 rows found
- Estimate 산업: 14 rows found
- Estimate 임업: 10 rows found
- Total: 90 order entries scanned across 4 pages

### 2026-01-15: Download Logic Bug - List Page Saved Instead of Detail Page

**Problem**: Downloaded HTML files contained the **list page** instead of the **detail page** content. `local_file_processor.py` returned 0 rows because the expected data table wasn't present.

**Root Cause Analysis**:
1. 영림 OMS의 "조회" 버튼 클릭 시 JavaScript `window.open()`으로 새 팝업 창이 열림
2. Selenium이 새 창 핸들을 감지하지 못함 (Edge 브라우저 팝업 차단 또는 타이밍 이슈)
3. Fallback 로직이 URL 변경 없음을 감지하고 현재 페이지(목록) HTML을 저장

**JavaScript Button Behavior** (영림 OMS):
```javascript
// ledger (trans_link) 버튼
$("body").on("click", ".trans_link", function() {
    window.open('/oms/trans_doc.jsp?chulhano='+$(this).attr("chulhano")+'&younglim_gubun='+$("#younglim_gubun").val());
});

// estimate (estimate_link) 버튼
$("body").on("click", ".estimate_link", function() {
    window.open('/oms/estimate_doc.jsp?ordno='+$(this).attr("ordno")+'&younglim_gubun='+$("#younglim_gubun").val());
});
```

**Solution**: 버튼 클릭 대신 **직접 URL 네비게이션** 방식으로 변경
- Modified [v10_auto_server.py:435-478](v10_auto_server.py#L435-L478)
- 상세 페이지 URL을 직접 구성하여 `driver.get()` 호출
- 팝업 차단 문제 완전히 회피

**Code Change**:
```python
# 변경 전: 버튼 클릭 (팝업 문제 발생)
button_element.click()

# 변경 후: 직접 URL 네비게이션
if button_type == "ledger":
    detail_url = f"http://door.yl.co.kr/oms/trans_doc.jsp?chulhano={button_id}&younglim_gubun={younglim_gubun}"
else:
    detail_url = f"http://door.yl.co.kr/oms/estimate_doc.jsp?ordno={button_id}&younglim_gubun={younglim_gubun}"
browser_manager.driver.get(detail_url)
```

**Key Insight**:
- 웹 자동화에서 `window.open()` 팝업은 브라우저 설정, 팝업 차단기 등에 따라 불안정함
- 가능하면 버튼 클릭 대신 직접 URL 구성으로 네비게이션하는 것이 안정적
- URL 파라미터는 HTML에서 파싱한 버튼 속성(`chulhano`, `ordno`)과 페이지 URL의 쿼리 파라미터(`younglim_gubun`)를 조합

**Edge Browser Session Disconnection**:
- 다운로드 중 Edge 브라우저 세션이 끊어지는 현상 발생
- 에러: `invalid session id: session deleted as the browser has closed the connection`
- **원인**: 장시간 자동화 중 브라우저 연결 불안정 또는 수동으로 브라우저 닫음
- **해결**: Edge 브라우저 재시작 후 V10 서버 재시작 필요
### 2026-01-15: Filename Collision & Force Download for Specific Date

**Problem**: 
1. `order_no`가 날짜(예: `26-01-15`)인 경우, 여러 주문이 같은 번호를 공유하여 파일 덮어쓰기가 발생함. 최종적으로 각 카테고리별로 1개의 파일만 남는 현상 확인.
2. 특정 날짜 데이터만 긴급히 다운로드해야 하는 상황에서 전체 다운로드 로직은 비효율적임.

**Root Cause**:
- `v10_auto_server.py` 및 `run_download_once.py`에서 `order_no`를 파일명으로 사용함.
- 영림 OMS에서는 주문번호(`order_no`)가 날짜로 표시되는 경우가 많아 고유성이 보장되지 않음.

**Solution**:
1. **파일명 고유성 확보**: `order_no` 뒤에 버튼의 고유 ID(`chulhano` 또는 `ordno`)를 추가하여 저장 (`{order_no}_{button_id}.html`).
2. **날짜 필터링 및 강제 다운로드**: 특정 날짜 문자열이 포함된 주문만 필터링하고, `distributed_lock` 및 `local_history`를 무시(Bypass)하는 `FORCED DOWNLOAD MODE` 구현.

**Code Change (Filename)**:
```python
# 변경 전
filename = f"{order_no}.html"

# 변경 후
filename = f"{order_no}_{button_id}.html"
```

**Key Insight**:
- 웹에서 보이는 "주문번호"가 시스템 내부적으로 항상 고유(Unique)하지 않을 수 있음.
- 파일 저장 시에는 반드시 고유한 ID(Primary Key 역할을 하는 속성)를 파일명에 조합해야 데이터 유실을 방지할 수 있음.

---

### 2026-01-15: Web Dashboard Integration & Port Conflict Issues

**Context**: 
대시보드에 수동 다운로드 제어 및 업로드 버튼 분리 기능을 통합하는 과정에서 Flask 서버 접속 불가 문제 발생.

**Problem**:
1. **포트 충돌**: `http://localhost:5080` 접속 시 연결 실패. `netstat` 확인 결과 5080 포트가 여러 프로세스(PID)에 의해 중복 점유됨.
2. **잔류 세션**: `kill_processes.bat`으로 프로세스를 종료해도 `CLOSE_WAIT`, `FIN_WAIT_2` 상태의 TCP 연결이 남아 새 서버 실행 시 충돌 발생.
3. **근본 원인**: Windows 환경에서 프로세스 강제 종료 후에도 네트워크 스택이 즉시 정리되지 않아 포트가 해제되지 않음.

**Solution Implemented**:
1. **자동 포트 정리 로직**: `v10_auto_server.py`에 `cleanup_port()` 함수 추가. 서버 시작 전 해당 포트를 점유한 프로세스를 자동으로 탐지하고 종료.
   ```python
   def cleanup_port(port):
       cmd = f"netstat -ano | findstr :{port}"
       output = subprocess.check_output(cmd, shell=True).decode()
       for line in output.strip().split('\n'):
           if 'LISTENING' in line:
               pid = line.strip().split()[-1]
               os.system(f"taskkill /F /PID {pid} /T")
   ```
2. **프로세스 정리 스크립트**: `kill_processes.bat` 생성하여 Python 및 Edge 프로세스를 일괄 종료.

**Partial Solution (Requires System Restart)**:
- 자동 포트 정리 로직만으로는 완전히 해결되지 않음. 잔류 TCP 세션이 남아있는 경우 **시스템 재시작**이 필요함.
- 재시작 후 `start_edge_debug.bat` → `run_v10_server.bat` 순서로 실행하면 정상 작동.

**Dashboard Enhancements**:
1. **수동 다운로드 버튼**: [📩 Manual Download], [🔥 Force Sync (Bypass)] 추가.
2. **업로드 버튼 분리**: 원장/견적 업로드 버튼을 각각 배치하고, 처리할 파일이 있을 때만 활성화.
3. **고유 파일명 시스템**: `{order_no}_{button_id}.html` 형식으로 저장하여 동일 날짜 주문 덮어쓰기 방지.

**Future Improvements Needed**:
1. **포트 충돌 근본 해결**: 
   - Flask 서버 시작 전 포트 상태를 더 정확히 체크하고, 필요 시 대기 시간(grace period)을 두어 TCP 세션이 완전히 종료될 때까지 기다림.
   - 또는 동적 포트 할당 방식 검토 (5080 고정 대신 사용 가능한 포트 자동 선택).
2. **서버 재시작 자동화**: 
   - 포트 충돌 감지 시 자동으로 기존 프로세스를 종료하고 재시작하는 로직 추가.
3. **Health Check 엔드포인트**: 
   - `/health` 엔드포인트를 추가하여 서버가 정상적으로 응답하는지 확인할 수 있도록 개선.

**Key Insight**:
- Windows 환경에서는 프로세스 종료 후에도 네트워크 리소스가 즉시 해제되지 않을 수 있음.
- 개발 환경에서는 시스템 재시작이 가장 확실한 해결책이지만, 프로덕션 환경을 고려하면 더 견고한 포트 관리 메커니즘이 필요함.
- Flask 개발 서버 대신 프로덕션 WSGI 서버(예: Waitress, Gunicorn) 사용을 검토할 필요가 있음.
