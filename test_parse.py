"""Test parsing of downloaded HTML files"""
from local_file_processor import process_html_file
from pathlib import Path

# Test ledger file parsing
ledger_file = Path('data/downloads/ledger/26-01-15.html')
print(f'Processing {ledger_file}...')
data = process_html_file(str(ledger_file), 'ledger')
print(f'Ledger rows: {len(data)}')
if data:
    print(f'First row columns: {len(data[0])}')
    print(f'Sample (first 5 cols): {data[0][:5]}')

# Test estimate file parsing
estimate_file = Path('data/downloads/estimate/2026-01-15.html')
print(f'\nProcessing {estimate_file}...')
data2 = process_html_file(str(estimate_file), 'estimate')
print(f'Estimate rows: {len(data2)}')
if data2:
    print(f'First row columns: {len(data2[0])}')
    print(f'Sample (first 5 cols): {data2[0][:5]}')
