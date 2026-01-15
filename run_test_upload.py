
import os
import sys
import time
from pathlib import Path
import local_file_processor
from erp_upload_automation_v2 import ErpUploadAutomation

def main():
    # Define paths
    base_dir = Path(r"c:\Users\DS-Sales0\shop_ver20")
    ledger_dir = base_dir / "data" / "downloads" / "ledger"
    target_file = ledger_dir / "26-01-15.html"
    
    print(f"Targeting file: {target_file}")
    
    if not target_file.exists():
        print(f"Error: File not found at {target_file}")
        return

    # Process the file locally
    print("Parsing HTML file...")
    erp_data = local_file_processor.process_html_file(str(target_file), target_type='ledger')
    
    if not erp_data:
        print("No data extracted from file.")
        return
        
    print(f"Extracted {len(erp_data)} rows.")
    
    # Run Automation
    print("Starting ERP Upload Automation...")
    automation = ErpUploadAutomation()
    try:
        # Check if we can maximize the window
        # We need to start browser first? run() does it.
        # But run() does everything.
        
        # automation.run manages the lifecycle.
        success = automation.run(direct_data=erp_data, auto_close=False, target_type='ledger')
        
        if success:
            print("Upload completed successfully.")
        else:
            print("Upload failed.")
            if automation.page:
                try:
                    timestamp = time.strftime('%H%M%S')
                    debug_file = base_dir / "logs" / "uploader" / f"debug_source_{timestamp}.html"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(automation.page.content())
                    print(f"Saved page source to {debug_file}")
                    
                    # Also list frames
                    print("Frames:")
                    for frame in automation.page.frames:
                        print(f" - Name: {frame.name}, URL: {frame.url}")
                except Exception as e:
                    print(f"Failed to save debug info: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close manually if needed
        automation.close()

if __name__ == "__main__":
    main()
