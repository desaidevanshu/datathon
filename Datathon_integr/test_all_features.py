"""
COMPREHENSIVE TEST - Say YES to All Features
Route: CSMT → BKC
"""
import subprocess
import sys

# Test all features by saying YES
inputs = """CSMT
BKC
y

1.5
y
Heavy traffic near BKC junction due to ongoing metro construction work
High
n
n
"""

print("="*70)
print("FULL FEATURE TEST: CSMT → BKC")
print("Testing ALL features:")
print("  1. Community Reports")
print("  2. Nearby Stations")
print("  3. Weather & Events")
print("  4. Traffic Prediction")
print("  5. Bottleneck Forecast")
print("  6. Smart Recommendations")
print("  7. What-If Simulator (blank weather, 1.5x traffic)")
print("  8. Submit Report")
print("="*70)

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
    
    # Save output
    with open('complete_test_output.txt', 'w', encoding='utf-8', errors='replace') as f:
        f.write(output)
    
    print("\n✓ Test completed! Output saved to: complete_test_output.txt")
    print(f"Total output: {len(output)} characters\n")
    
    # Parse and display each section
    lines = output.split('\n')
    
    sections = {
        "Community Reports": "COMMUNITY REPORTS",
        "Nearby Stations": "NEARBY STATIONS",
        "Weather Data": "Weather:",
        "Traffic Sensors": "Traffic:",
        "Prediction": "FORECAST",
        "Bottleneck": "BOTTLENECK FORECAST",
        "Smart Recommendations": "SMART RECOMMENDATIONS",
        "What-If Simulator": "WHAT-IF SIMULATOR",
        "What-If Result": "WHAT-IF RESULT",
        "Report Submitted": "Report submitted"
    }
    
    print("="*70)
    print("FEATURE VERIFICATION")
    print("="*70)
    
    for feature, keyword in sections.items():
        found = keyword in output
        status = "✓ FOUND" if found else "✗ MISSING"
        print(f"{status}: {feature}")
    
    # Show What-If result if found
    if "WHAT-IF RESULT" in output:
        print("\n" + "="*70)
        print("WHAT-IF SIMULATION RESULT:")
        print("="*70)
        start = output.find(">>> WHAT-IF RESULT")
        end = output.find("Submit traffic report", start)
        if end == -1:
            end = start + 400
        result = output[start:end]
        for line in result.split('\n')[:10]:
            if line.strip():
                print(line)
    
    # Check for errors
    error_lines = [l for l in lines if 'Error:' in l and 'InconsistentVersion' not in l]
    if error_lines:
        print("\n" + "="*70)
        print("ERRORS DETECTED:")
        print("="*70)
        for err in error_lines[:5]:
            print(err.strip())
    else:
        print("\n" + "="*70)
        print("✓ NO CRITICAL ERRORS - ALL SYSTEMS OPERATIONAL!")
        print("="*70)

except subprocess.TimeoutExpired:
    print("ERROR: Test timed out after 120s")
    proc.kill()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
