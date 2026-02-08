"""
REAL END-TO-END TEST - Actually runs all features
"""
import subprocess
import sys

print("="*70)
print("COMPREHENSIVE REAL TEST - All New Features")
print("="*70)

# Prepare inputs that will test ALL features
inputs = """CSMT
Dadar
n
y
Rain
1.5
y
Heavy construction on Eastern Express Highway causing major delays
High
n
n
"""

print("\nTest Scenario:")
print("-" * 70)
print("Route: CSMT → Dadar")
print("Community Report: Check existing reports")
print("What-If: Change weather to Rain, increase traffic by 50%")
print("Submit Report: 'Heavy construction on Eastern Express Highway'")
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
    
    # Save full output to file for inspection
    with open('test_output.txt', 'w', encoding='utf-8', errors='replace') as f:
        f.write(output)
    
    print("\n✓ Full output saved to: test_output.txt")
    
    # Extract and display key sections
    lines = output.split('\n')
    
    # Find community reports section
    print("\n" + "="*70)
    print("1. COMMUNITY REPORTS SECTION")
    print("="*70)
    in_community = False
    for line in lines:
        if 'COMMUNITY REPORTS' in line:
            in_community = True
        elif in_community and ('Nearby Stations' in line or 'SYSTEM' in line):
            break
        if in_community:
            print(line)
    
    # Find What-If section
    print("\n" + "="*70)
    print("2. WHAT-IF SIMULATION SECTION")
    print("="*70)
    in_whatif = False
    for line in lines:
        if 'WHAT-IF SIMULATOR' in line:
            in_whatif = True
        elif in_whatif and 'Submit traffic report' in line:
            break
        if in_whatif and line.strip():
            print(line)
    
    # Find report submission
    print("\n" + "="*70)
    print("3. REPORT SUBMISSION CONFIRMATION")
    print("="*70)
    for line in lines:
        if 'Report submitted' in line or 'Thank you' in line:
            print(line)
    
    # Verification
    print("\n" + "="*70)
    print("FEATURE VERIFICATION")
    print("="*70)
    
    checks = {
        "Community Reports Displayed": "COMMUNITY REPORTS" in output,
        "What-If Simulator Ran": "WHAT-IF SIMULATOR" in output or "WHAT-IF RESULT" in output,
        "Scenario Modified": ("Rain" in output or "multiplier" in output),
        "Report Submitted": "Report submitted" in output or "anonymously" in output,
    }
    
    all_pass = True
    for feature, passed in checks.items():
        status = "✓ WORKING" if passed else "✗ FAILED"
        print(f"{status}: {feature}")
        if not passed:
            all_pass = False
    
    if all_pass:
        print("\n" + "="*70)
        print("🎉 ALL FEATURES VERIFIED AND WORKING!")
        print("="*70)
    else:
        print("\n⚠ Some features may need debugging")
        print("Check test_output.txt for full details")

except subprocess.TimeoutExpired:
    print("ERROR: Test timed out after 120s")
    proc.kill()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
