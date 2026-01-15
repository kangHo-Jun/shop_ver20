import sys
import os
import time
import logging

# Ensure we can import from current directory
sys.path.append(os.getcwd())

from v10_auto_server import AutoDownloader, browser_manager, distributed_lock, server_status
from logging_config import logger

# Set up console handler for immediate feedback
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def main():
    logger.info("Starting manual download cycle...")
    
    # Initialize components (mimicking main block of server)
    try:
        logger.info("Connecting to Distributed Lock Manager...")
        if distributed_lock.connect():
            server_status["lock_manager_connected"] = True
            server_status["machine_id"] = distributed_lock.machine_id
            logger.info(f"Distributed lock connected: {distributed_lock.machine_id}")
        else:
            logger.warning("Distributed lock failed to connect. Running in standalone mode.")
            
    except Exception as e:
        logger.warning(f"Warning: Lock manager init failed: {e}")

    # Initialize browser
    try:
        logger.info("Connecting to Browser...")
        browser_manager.launch()
    except Exception as e:
        logger.error(f"Failed to launch/connect browser: {e}")
        return

    # Run download cycle
    downloader = AutoDownloader()
    
    # OVERRIDE: Force download by mocking the check method
    # We will Monkey Patch the download_from_page method for this specific run
    original_download_method = downloader.download_from_page
    
    def force_download_wrapper(list_url, save_dir, doc_type):
        logger.info(f"*** FORCED DOWNLOAD MODE: Processing {list_url} ***")
        browser_manager.navigate(list_url)
        time.sleep(2)

        html_source = browser_manager.get_source()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')

        rows = soup.select("table tbody tr")
        logger.info(f"[Downloader] Found {len(rows)} rows in table")

        downloaded_count = 0

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3: continue

            order_no = cols[0].get_text(strip=True)
            if not order_no: continue

            # V10: Check distributed lock BEFORE checking local history
            # MODIFIED: Only download if order_no corresponds to "26-01-15"
            target_date_str = "26-01-15"
            
            if target_date_str not in order_no:
                logger.info(f"[Skipping] {order_no} (Does not match {target_date_str})")
                continue

            # BYPASS LOCK AND HISTORY CHECKS FOR TARGET DATE
            logger.info(f"[Force Download] Processing {order_no} (Matches {target_date_str})")

            try:
                # Find download button (Copy-paste logic from original but simplified)
                button_col = cols[-1] if len(cols) > 0 else None
                if not button_col: continue

                button = button_col.find("button", class_="trans_link")
                button_type = "ledger"
                button_attr = "chulhano"

                if not button:
                    button = button_col.find("button", class_="estimate_link")
                    button_type = "estimate"
                    button_attr = "ordno"

                if not button:
                    logger.warning(f"No button for {order_no}")
                    continue

                button_id = button.get(button_attr, "")
                
                # URL Parsing
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(list_url)
                params = parse_qs(parsed.query)
                younglim_gubun = params.get('younglim_gubun', [''])[0]

                # Direct Navigation
                original_url = browser_manager.driver.current_url
                if button_type == "ledger":
                    detail_url = f"http://door.yl.co.kr/oms/trans_doc.jsp?chulhano={button_id}&younglim_gubun={younglim_gubun}"
                else: 
                    detail_url = f"http://door.yl.co.kr/oms/estimate_doc.jsp?ordno={button_id}&younglim_gubun={younglim_gubun}"

                logger.info(f"Downloading {order_no}...")
                browser_manager.driver.get(detail_url)
                time.sleep(1.5) # Slightly faster

                detail_html = browser_manager.get_source()
                
                # Return to list
                browser_manager.driver.get(original_url)
                
                # Save
                # MODIFIED: Append button_id to ensure uniqueness for same-day orders
                filename = f"{order_no}_{button_id}.html"
                filepath = save_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(detail_html)
                
                logger.info(f"[Saved] {filepath}")
                downloaded_count += 1
                
                # Update Lock to Completed anyway (to ensure future consistency)
                try:
                    distributed_lock.release_lock(order_no, status="completed", notes="Forced Download")
                except: pass

            except Exception as e:
                logger.error(f"Error on {order_no}: {e}")
                try:
                    browser_manager.driver.get(list_url)
                except: pass
                continue
                
        return downloaded_count

    # Apply Monkey Patch
    downloader.download_from_page = force_download_wrapper
    
    downloader.activate() # Sets active_mode = True
    
    logger.info("Running FORCED download cycle...")
    downloader.download_cycle()
    logger.info("Download cycle complete.")

if __name__ == "__main__":
    main()
