import sys
import argparse
from datetime import datetime
from lock_manager import DistributedLockManager

def list_locks(limit=20):
    """최근 락 기록 조회"""
    manager = DistributedLockManager()
    if not manager.connect():
        print("[오류] Google Sheets 연결 실패")
        return

    print(f"\n[최근 {limit}개 락 기록 조회]")
    print("-" * 80)
    print(f"{'Order ID':<20} | {'Status':<12} | {'Locked At':<25} | {'Machine':<15}")
    print("-" * 80)

    try:
        # 모든 레코드 가져오기
        records = manager.get_all_locks()
        
        # 역순 정렬 (최신순)
        records.reverse()
        
        count = 0
        for row in records:
            if count >= limit:
                break
                
            # Dictionary 키는 헤더 이름에 따라 다를 수 있으므로 인덱스나 키 확인 필요
            # gspread의 get_all_records()는 첫 행을 키로 사용
            order_id = row.get('order_id', '')
            status = row.get('status', '')
            locked_at = row.get('locked_at', '')
            machine = row.get('machine_id', '')
            
            print(f"{order_id:<20} | {status:<12} | {locked_at:<25} | {machine:<15}")
            count += 1
            
        print("-" * 80)
        print(f"총 {len(records)}개의 기록 중 {count}개 표시됨")

    except Exception as e:
        print(f"[오류] 데이터 조회 중 에러 발생: {e}")

def delete_lock(order_id):
    """특정 주문 락 삭제"""
    manager = DistributedLockManager()
    if not manager.connect():
        print("[오류] Google Sheets 연결 실패")
        return

    print(f"\n[락 삭제 시도] Order ID: {order_id}")
    
    # 해당 주문의 행 찾기
    row_num = manager._find_order_row(order_id)
    if not row_num:
        print(f"[실패] 해당 주문 ID({order_id})를 찾을 수 없습니다.")
        return

    try:
        # 행 삭제
        manager.lock_worksheet.delete_rows(row_num)
        print(f"[성공] 락 기록이 삭제되었습니다. 이제 재다운로드 가능합니다.")
    except Exception as e:
        print(f"[오류] 삭제 중 에러 발생: {e}")

def clear_date(target_date):
    """특정 날짜의 모든 락 삭제"""
    manager = DistributedLockManager()
    if not manager.connect():
        print("[오류] Google Sheets 연결 실패")
        return

    print(f"\n[날짜별 일괄 삭제] 대상 날짜: {target_date} (YYYY-MM-DD)")
    confirm = input("정말로 해당 날짜의 모든 락 기록을 삭제하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("취소되었습니다.")
        return

    try:
        all_values = manager.lock_worksheet.get_all_values()
        header = all_values[0]
        rows_to_delete = []
        
        # 날짜 형식 체크 (YYYY-MM-DD)
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            print("[오류] 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식이어야 합니다.")
            return

        print("데이터 검색 중...")
        for idx, row in enumerate(all_values[1:], start=2):
            if len(row) < 3:
                continue
                
            locked_at_str = row[2] # 3번째 컬럼이 locked_at
            try:
                # ISO 포맷 (2026-01-15T08:33:21.978436)에서 날짜 추출
                locked_dt = datetime.fromisoformat(locked_at_str).date()
                
                if locked_dt == target_dt:
                    rows_to_delete.append(idx)
            except:
                continue
        
        if not rows_to_delete:
            print("[알림] 해당 날짜의 기록을 찾을 수 없습니다.")
            return
            
        print(f"총 {len(rows_to_delete)}개의 기록을 찾았습니다. 삭제를 시작합니다...")
        
        # 역순 삭제
        for row_num in sorted(rows_to_delete, reverse=True):
            manager.lock_worksheet.delete_rows(row_num)
            print(f"삭제됨: 행 {row_num}")
            
        print(f"[성공] {len(rows_to_delete)}개의 락 기록이 삭제되었습니다.")

    except Exception as e:
        print(f"[오류] 일괄 삭제 중 에러 발생: {e}")

def main():
    parser = argparse.ArgumentParser(description='V10 Distributed Lock Manager Utility')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    parser_list = subparsers.add_parser('list', help='List recent locks')
    parser_list.add_argument('--limit', type=int, default=20, help='Number of records to show')

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a specific lock')
    parser_delete.add_argument('order_id', help='Order ID to delete')

    # Clear Date command
    parser_clear = subparsers.add_parser('clear_date', help='Clear all locks for a specific date')
    parser_clear.add_argument('date', help='Date to clear (YYYY-MM-DD)')

    args = parser.parse_args()

    if args.command == 'list':
        list_locks(args.limit)
    elif args.command == 'delete':
        delete_lock(args.order_id)
    elif args.command == 'clear_date':
        clear_date(args.date)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
