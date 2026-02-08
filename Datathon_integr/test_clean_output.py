"""Quick test to verify clean output"""
import subprocess
import sys

inputs = """CSMT
BKC
n
n
n
"""

proc = subprocess.Popen(
    [sys.executable, '-u', 'interactive_tester.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

try:
    output, _ = proc.communicate(input=inputs, timeout=60)
    
    print("="*70)
    print("CLEAN OUTPUT TEST")
    print("="*70)
    
    # Check for warnings
    warning_count = output.count('UserWarning')
    
    if warning_count == 0:
        print("\n✓ NO SKLEARN WARNINGS - Output is clean!\n")
    else:
        print(f"\n⚠ Still {warning_count} warnings found\n")
    
    # Show key sections without warnings
    lines = output.split('\n')
    
    print("\nSample Output (warnings filtered):")
    print("-" * 70)
    for line in lines[15:30]:  # Show main section
        if 'UserWarning' not in line and 'sklearn' not in line and line.strip():
            print(line)
    
except Exception as e:
    print(f"Test error: {e}")
