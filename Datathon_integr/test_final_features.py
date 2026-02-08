"""
FINAL COMPREHENSIVE TEST - With VALID Route
"""
import subprocess
import sys

print("="*70)
print("FINAL REAL TEST - Valid Route CSMT → BKC")
print("="*70)

# Use VALID destinations from dataset
inputs = """CSMT
BKC
n
y
Rain
1.5
y
Heavy traffic due to construction near BKC
High
n
n
"""

print("\nTest Steps:")
print("1. Route: CSMT → BKC (VALID)")
print("2. Check Community Reports")
print("3. Run What-If: Rain + 1.5x traffic")
print("4. Submit Report about construction")
print("-" * 70)

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
    with open('final_test_output.txt', 'w', encoding='utf-8', errors='replace') as f:
        f.write(output)
    
    print(f"\n✓ Full output saved to: final_test_output.txt ({len(output)} bytes)")
    
    # Check each feature
    print("\n" + "="*70)
    print("FEATURE VERIFICATION")
    print("="*70)
    
    features = {
        "1. Community Reports Section": "COMMUNITY REPORTS" in output,
        "2. Prediction Completed": ("Prediction:" in output or "FORECAST" in output),
        "3. What-If Simulator Started": "WHAT-IF SIMULATOR" in output,
        "4. Weather Modified": "Rain" in output and "Weather" in output.split("WHAT-IF")[1] if "WHAT-IF" in output else False,
        "5. What-If Result Shown": "WHAT-IF RESULT" in output,
        "6. Impact Calculated": ("worse" in output or "better" in output) and "WHAT-IF" in output,
        "7. Report Submission Offered": "Submit traffic report" in output,
        "8. Report Confirmed": "Report submitted" in output or "anonymously" in output,
    }
    
    passed = 0
    failed = 0
    
    for feature, status in features.items():
        mark = "✓" if status else "✗"
        print(f"{mark} {feature}")
        if status:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{len(features)} features verified")
    print("="*70)
    
    if passed >= 6:
        print("\n🎉 MOST FEATURES WORKING! System is functional.")
    elif passed >= 4:
        print("\n⚠ Partial success - Some features working")
    else:
        print("\n❌ Multiple failures - Check output file")
    
    # Show snippets
    if "WHAT-IF RESULT" in output:
        print("\n" + "="*70)
        print("WHAT-IF RESULT SNIPPET:")
        print("="*70)
        result_start = output.find("WHAT-IF RESULT")
        if result_start > 0:
            snippet = output[result_start:result_start+300]
            print(snippet[:200])
    
except subprocess.TimeoutExpired:
    print("ERROR: Test timed out")
    proc.kill()
except Exception as e:
    print(f"ERROR: {e}")
