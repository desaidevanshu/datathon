"""
Full End-to-End Test of Interactive Tester
Captures complete output to verify all features work correctly.
"""
import subprocess
import sys

print("="*70)
print("FULL SYSTEM TEST - Interactive Traffic Forecaster")
print("="*70)
print("\nTest Route: CSMT → Gateway of India")
print("Input Simulation: Auto-answering prompts\n")

# Run interactive tester with automated inputs
proc = subprocess.Popen(
    [sys.executable, '-u', 'interactive_tester.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'  # Handle unicode errors
)

# Provide inputs
inputs = "CSMT\nGateway_of_India\nn\n"

try:
    output, _ = proc.communicate(input=inputs, timeout=120)
    
    # Split output into sections
    lines = output.split('\n')
    
    # Extract key sections
    print("\n" + "="*70)
    print("CAPTURED OUTPUT")
    print("="*70)
    
    in_stations = False
    in_forecast = False
    in_bottleneck = False
    in_recommendations = False
    
    for line in lines:
        # Print all non-warning lines for clarity
        if 'warning' in line.lower() or 'inconsistent' in line.lower():
            continue
            
        # Detect sections
        if 'NEARBY STATIONS' in line:
            in_stations = True
            print("\n" + "="*70)
        elif 'FORECAST' in line and 'BOTTLENECK' not in line:
            in_forecast = True
            in_stations = False
            print("\n" + "="*70)
        elif 'BOTTLENECK FORECAST' in line:
            in_bottleneck = True
            in_forecast = False
            print("\n" + "="*70)
        elif 'SMART RECOMMENDATIONS' in line:
            in_recommendations = True
            in_bottleneck = False
            print("\n" + "="*70)
        elif 'Check another route' in line:
            in_recommendations = False
            print("\n" + "="*70)
        
        # Print important lines
        if any(keyword in line for keyword in [
            'STATIONS', 'Fuel', 'EV', 'FORECAST', 'Prediction',
            'Confidence', 'BOTTLENECK', 'RISING', 'EASING', 'STABLE',
            'ALERT', 'SMART', 'Route', 'BREAK', 'DEPARTURE', 'OPTIMAL',
            'clear', 'Wait', 'Leave'
        ]):
            print(line)
    
    print("\n" + "="*70)
    print("VALIDATION CHECKS")
    print("="*70)
    
    # Verify features are present
    checks = [
        ("Station Locator", "NEARBY STATIONS" in output or "Fuel Stations" in output),
        ("Congestion Forecast", "FORECAST" in output and "Prediction:" in output),
        ("Bottleneck Detection", "BOTTLENECK FORECAST" in output),
        ("Smart Recommendations", "SMART RECOMMENDATIONS" in output),
        ("Route Alert", "Route" in output and ("clear" in output or "ALERT" in output)),
        ("Departure Optimization", "OPTIMAL DEPARTURE" in output or "DEPARTURE:" in output),
    ]
    
    all_passed = True
    for feature, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {feature}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL FEATURES VERIFIED - SYSTEM WORKING CORRECTLY")
    else:
        print("⚠ SOME FEATURES MISSING - CHECK OUTPUT ABOVE")
    print("="*70)
    
except subprocess.TimeoutExpired:
    print("ERROR: Test timed out")
    proc.kill()
except Exception as e:
    print(f"ERROR: {e}")
