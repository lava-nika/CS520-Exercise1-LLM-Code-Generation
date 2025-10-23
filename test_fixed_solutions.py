#!/usr/bin/env python3
"""
Test script to verify that the fixed solutions actually work
"""

import subprocess
import sys
import tempfile
import os
import json
from pathlib import Path

# Load problems
WORKSPACE = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1")
with open(WORKSPACE / "selected_humaneval_problems.json", 'r') as f:
    problems = json.load(f)

problem_mapping = {
    "problem1": "HumanEval/0",
    "problem8": "HumanEval/32",
}

fixes_dir = WORKSPACE / "generated code" / "fixed_solutions"

print("=" * 80)
print("TESTING FIXED SOLUTIONS")
print("=" * 80)

fixed_files = list(fixes_dir.glob("*_FIXED.py"))
print(f"\nFound {len(fixed_files)} fixed solutions to test\n")

test_results = []

for fixed_file in sorted(fixed_files):
    print(f"Testing: {fixed_file.name}")
    
    problem_key = None
    if "problem1" in fixed_file.name:
        problem_key = "HumanEval/0"
    elif "problem8" in fixed_file.name:
        problem_key = "HumanEval/32"
    
    if not problem_key:
        print(f"Could not determine problem key")
        continue
    
    # Read the fixed code
    with open(fixed_file, 'r') as f:
        solution_code = f.read()
    
    # Get test code
    problem_data = problems[problem_key]
    test_code = problem_data['test']
    
    # Create temp file with solution and test
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(solution_code)
            f.write('\n\n')
            f.write(test_code)
            f.write('\n\n')
            f.write('if __name__ == "__main__":\n')
            f.write(f'    check({problem_data["entry_point"]})\n')
            f.write('    print("All tests passed!")\n')
            temp_file = f.name
        
        # Execute
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print(f"  PASSED - All tests passed!")
            test_results.append((fixed_file.name, True, "Success"))
        else:
            print(f"  FAILED")
            print(f"     Error: {result.stderr[:200]}")
            test_results.append((fixed_file.name, False, result.stderr[:200]))
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT")
        test_results.append((fixed_file.name, False, "Timeout"))
    except Exception as e:
        print(f" ERROR: {str(e)}")
        test_results.append((fixed_file.name, False, str(e)))
    
    print()

print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = sum(1 for _, success, _ in test_results if success)
failed = len(test_results) - passed

print(f"\nTotal Fixed Solutions Tested: {len(test_results)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed > 0:
    print("\nFailed Solutions:")
    for filename, success, error in test_results:
        if not success:
            print(f"  - {filename}: {error[:100]}")

improvement_rate = (passed / len(test_results) * 100) if test_results else 0
print(f"\nImprovement Rate: {improvement_rate:.1f}%")

if passed == len(test_results):
    print("\ All fixes successful.")
else:
    print("\n Some fixes still need work")
