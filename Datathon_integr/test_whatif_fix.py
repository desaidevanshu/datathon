"""Test What-If Simulator Fix"""
import subprocess
import sys

inputs = """CSMT
BKC
y
Rain
1.5
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
    output, _ = proc.communicate(input=inputs, timeout=120)
    
    if "WHAT-IF RESULT" in output:
        print("✓ WHAT-IF SIMULATOR WORKING!")
        
        # Extract result
        start = output.find("WHAT-IF RESULT")
        end = output.find("Submit traffic report", start)
        snippet = output[start:end]
        print("\n" + snippet[:500])
    else:
        print("✗ What-If not found")
        if "Error" in output:
            errors = [line for line in output.split('\n') if 'Error' in line and 'Warning' not in line]
            print("Errors:", errors[:3])
            
except Exception as e:
    print(f"Test failed: {e}")
