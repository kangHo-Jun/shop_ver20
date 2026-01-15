
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import local modules
import local_file_processor
from erp_upload_automation_v2 import ErpUploadAutomation
from config import config

def run_test():
    test_file = Path("test_download_2601020260.html")
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return

    logger.info(f"Adding test file: {test_file}")
    
    # 1. Parse content
    with open(test_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Try parsing as Ledger
    logger.info("Parsing as Ledger (Purchase Input)...")
    erp_data = local_file_processor.process_html_content(
        html_content, 
        file_path_hint=test_file.name, 
        target_type='ledger'
    )
    
    if not erp_data:
        logger.error("Failed to parse data!")
        return

    logger.info(f"Extracted {len(erp_data)} rows.")
    for i, row in enumerate(erp_data[:3]): # Show first 3 rows
        logger.info(f"Row {i+1}: {row}")

    # 2. Inject into Automation
    logger.info("Starting Automation Injection...")
    automation = ErpUploadAutomation()
    
    # Run with auto_close=False so user can see the result
    # It will paste data but NOT save.
    success = automation.run(
        direct_data=erp_data, 
        auto_close=False, 
        target_type='ledger'
    )
    
    if success:
        logger.info("Test Run Successfully Completed! Data should be pasted in the ERP popup.")
    else:
        logger.error("Test Run Failed.")

if __name__ == "__main__":
    run_test()
