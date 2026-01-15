import os
import sys
import time
from pathlib import Path
import local_file_processor
from erp_upload_automation_v2 import ErpUploadAutomation
import logging

# Set up logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_upload(file_path, doc_type):
    logger.info(f"--- Starting test for {doc_type}: {file_path.name} ---")
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    # 1. Parse HTML
    logger.info(f"Parsing {doc_type} HTML...")
    erp_data = local_file_processor.process_html_file(str(file_path), target_type=doc_type)
    
    if not erp_data:
        logger.error(f"No data extracted from {file_path.name}")
        return False
        
    logger.info(f"Extracted {len(erp_data)} rows.")

    # 2. ERP Upload
    logger.info(f"Initializing ERP Automation for {doc_type}...")
    automation = ErpUploadAutomation()
    try:
        # direct_data provides the parsed rows directly to the automation
        success = automation.run(direct_data=erp_data, auto_close=True, target_type=doc_type)
        if success:
            logger.info(f"✅ {doc_type.capitalize()} upload test successful!")
            return True
        else:
            logger.error(f"❌ {doc_type.capitalize()} upload test failed.")
            return False
    except Exception as e:
        logger.error(f"Exception during {doc_type} upload: {e}")
        return False
    finally:
        automation.close()

def main():
    base_dir = Path(os.getcwd())
    
    # Ledger Sample
    ledger_file = base_dir / "data" / "downloads" / "ledger" / "26-01-15_2601150136.html"
    
    # Estimate Sample
    estimate_file = base_dir / "data" / "downloads" / "estimate" / "2026-01-15_260115-006.html"

    # Test Ledger
    ledger_success = test_upload(ledger_file, 'ledger')
    
    # Wait a bit between tests
    time.sleep(3)
    
    # Test Estimate
    estimate_success = test_upload(estimate_file, 'estimate')

    if ledger_success and estimate_success:
        logger.info("=" * 40)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 40)
    else:
        logger.error("=" * 40)
        logger.error("SOME TESTS FAILED. CHECK LOGS.")
        logger.error("=" * 40)

if __name__ == "__main__":
    main()
