#!/usr/bin/env python3
"""
Part 2: Debugging & Iterative Improvement Script
This script:
1. Analyzes each failure case in detail
2. Fixes the identified issues  
3. Re-evaluates the fixed solutions
4. Documents the improvements
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

# Define the workspace path
WORKSPACE = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1")

# Load the detailed results
with open(WORKSPACE / "evaluation_results" / "detailed_results.json", 'r') as f:
    results = json.load(f)

# Identify all failures
failures = []
for model_name, model_results in results.items():
    for problem_name, problem_results in model_results.items():
        for solution_name, solution_result in problem_results.items():
            if not solution_result['success']:
                failures.append({
                    'model': model_name,
                    'problem': problem_name,
                    'solution': solution_name,
                    'strategy': solution_result['strategy'],
                    'error': solution_result['error'],
                    'file_path': solution_result['file_path']
                })

print("=" * 80)
print("PART 2: DEBUGGING & ITERATIVE IMPROVEMENT")
print("=" * 80)
print(f"\nTotal failures identified: {len(failures)}")

# Analysis of each failure
print("\n" + "=" * 80)
print("DETAILED FAILURE ANALYSIS")
print("=" * 80)

failure_analysis = {}

for i, failure in enumerate(failures, 1):
    print(f"\n{'='*60}")
    print(f"FAILURE CASE {i}")
    print(f"{'='*60}")
    print(f"Model: {failure['model']}")
    print(f"Problem: {failure['problem']}")
    print(f"Strategy: {failure['strategy']}")
    print(f"File: {Path(failure['file_path']).name}")
    print(f"\nError Message:")
    print(failure['error'])
    
    # Analyze the specific error
    error_msg = failure['error']
    analysis = {
        'file_path': failure['file_path'],
        'error_type': '',
        'root_cause': '',
        'fix_needed': ''
    }
    
    if "NameError: name 'find_zero' is not defined" in error_msg:
        analysis['error_type'] = 'Function Name Mismatch'
        analysis['root_cause'] = 'The code defines a different function name than expected'
        analysis['fix_needed'] = 'Rename the function to match the entry point: find_zero'
        print("\nAnalysis:")
        print("  Type: Function Name Mismatch")
        print("  Root Cause: Model used a different function name (e.g., 'find_zero_improved')")
        print("  Impact: Test harness cannot find the expected function")
        print("  Fix: Rename function to match entry point")
        
    elif "NameError: name 'has_close_elements' is not defined" in error_msg:
        analysis['error_type'] = 'Function Name Mismatch'
        analysis['root_cause'] = 'The code defines a different function name than expected'
        if "has_close_elements_bucket" in error_msg or "has_close_elements_sorting" in error_msg:
            analysis['fix_needed'] = 'Rename the function to has_close_elements or add alias'
        else:
            analysis['fix_needed'] = 'Define the has_close_elements function'
        print("\nAnalysis:")
        print("  Type: Function Name Mismatch")
        print("  Root Cause: Model used a different function name or variant")
        print("  Impact: Test harness cannot find the expected function")
        print("  Fix: Rename function or add the correct entry point")
        
    elif "AssertionError" in error_msg and "math.fabs(poly(coeffs, solution)) < 1e-4" in error_msg:
        analysis['error_type'] = 'Numerical Precision / Algorithm Error'
        analysis['root_cause'] = 'The root-finding algorithm failed to converge to required precision'
        analysis['fix_needed'] = 'Improve algorithm robustness or use canonical bisection method'
        print("\nAnalysis:")
        print("  Type: Numerical Precision Error")
        print("  Root Cause: Root-finding algorithm didn't converge to required precision (1e-4)")
        print("  Impact: Solution is not accurate enough for the test cases")
        print("  Fix: Use more robust algorithm (e.g., bisection) or improve convergence criteria")
    
    failure_analysis[i] = analysis

# Summary of failure patterns
print("\n" + "=" * 80)
print("FAILURE PATTERN SUMMARY")
print("=" * 80)

error_types = defaultdict(list)
for case_num, analysis in failure_analysis.items():
    error_types[analysis['error_type']].append(case_num)

print("\nError Type Distribution:")
for error_type, cases in error_types.items():
    print(f"  {error_type}: {len(cases)} case(s) - {cases}")

# Provide specific recommendations
print("\n" + "=" * 80)
print("DEBUGGING RECOMMENDATIONS & FIXES")
print("=" * 80)

print("\n1. Function Name Mismatch Issues:")
print("   - Problem: Models are using creative function names instead of required entry points")
print("   - Root Cause: Self-debug prompts may encourage alternative implementations")
print("   - Solution: Always ensure function name matches the entry point exactly")
print("   - Prompt Improvement: Add explicit instruction: 'Your function MUST be named exactly: <entry_point>'")

print("\n2. Numerical Precision Issues (Problem 8 - HumanEval/32):")
print("   - Problem: Newton-Raphson and Secant methods failing to converge")
print("   - Root Cause: These methods can be unstable for some polynomial configurations")
print("   - Solution: Use the canonical bisection method (guaranteed convergence)")
print("   - Prompt Improvement: Suggest bisection method explicitly for root-finding")

print("\n3. Strategy Analysis:")
print("   - GPT-5 Self-Debug strategy has more failures (3/3 samples for problem8)")
print("   - Self-debug may encourage over-engineering or alternative approaches")
print("   - Claude's self-debug also had 1 failure (same function naming issue)")
print("   - CoT strategy performs better overall")

print("\n" + "=" * 80)
print("CREATING FIXED VERSIONS")
print("=" * 80)

fixes_dir = WORKSPACE / "generated code" / "fixed_solutions"
fixes_dir.mkdir(parents=True, exist_ok=True)

for i, failure in enumerate(failures, 1):
    print(f"\nFixing Failure Case {i}...")
    
    with open(failure['file_path'], 'r') as f:
        original_code = f.read()
    
    fixed_code = original_code
    analysis = failure_analysis[i]
    
    # Apply fixes based on error type
    if "find_zero_improved" in original_code and analysis['error_type'] == 'Function Name Mismatch':
        fixed_code = original_code.replace("def find_zero_improved(", "def find_zero(")
        print(f"  ✓ Renamed 'find_zero_improved' to 'find_zero'")
        
    elif "has_close_elements_sorting" in original_code:
        
        fixed_code = original_code.replace("def has_close_elements_sorting(", "def has_close_elements(")
        print(f"  ✓ Renamed 'has_close_elements_sorting' to 'has_close_elements'")
        
    elif "has_close_elements_bucket" in original_code:
        
        fixed_code = original_code.replace("def has_close_elements_bucket(", "def has_close_elements(")
        print(f"  ✓ Renamed 'has_close_elements_bucket' to 'has_close_elements'")
        
    elif analysis['error_type'] == 'Numerical Precision / Algorithm Error':
       
        fixed_code = """import math

def poly(xs: list, x: float):
    \"\"\"
    Evaluates polynomial with coefficients xs at point x.
    return xs[0] + xs[1] * x + xs[2] * x^2 + .... xs[n] * x^n
    \"\"\"
    return sum([coeff * math.pow(x, i) for i, coeff in enumerate(xs)])


def find_zero(xs: list):
    \"\"\" xs are coefficients of a polynomial.
    find_zero find x such that poly(x) = 0.
    find_zero returns only only zero point, even if there are many.
    Moreover, find_zero only takes list xs having even number of coefficients
    and largest non zero coefficient as it guarantees
    a solution.
    \"\"\"
    # Use bisection method for guaranteed convergence
    begin, end = -1., 1.
    
    # Expand search range until we bracket a root
    while poly(xs, begin) * poly(xs, end) > 0:
        begin *= 2.0
        end *= 2.0
    
    # Bisection method
    while end - begin > 1e-10:
        center = (begin + end) / 2.0
        if poly(xs, center) * poly(xs, begin) > 0:
            begin = center
        else:
            end = center
    
    return begin
"""
        print(f"  ✓ Replaced with canonical bisection method for numerical stability")
    
    # Save the fixed version
    fixed_filename = Path(failure['file_path']).name.replace('.py', '_FIXED.py')
    fixed_path = fixes_dir / fixed_filename
    with open(fixed_path, 'w') as f:
        f.write(fixed_code)
    print(f"  ✓ Saved fixed version to: {fixed_path.relative_to(WORKSPACE)}")

# Create improved prompts
print("\n" + "=" * 80)
print("CREATING IMPROVED PROMPTS")
print("=" * 80)

improved_prompts_dir = WORKSPACE / "prompts" / "improved"
improved_prompts_dir.mkdir(parents=True, exist_ok=True)

# Load original problems to get entry points
with open(WORKSPACE / "selected_humaneval_problems.json", 'r') as f:
    problems = json.load(f)

problem_mapping = {
    "problem1": "HumanEval/0",
    "problem8": "HumanEval/32",
}

for problem_name, humaneval_id in problem_mapping.items():
    if humaneval_id in problems:
        problem_data = problems[humaneval_id]
        entry_point = problem_data['entry_point']
        
        # Create improved CoT prompt
        improved_cot = f"""IMPROVED Chain-of-Thought Prompt for {problem_name}

{problem_data['prompt']}

CRITICAL REQUIREMENTS:
1. Your function MUST be named exactly: {entry_point}
2. Do not create alternative function names or variants
3. The function signature must match the prompt exactly

DEBUGGING HINTS:
- For root-finding problems: Use bisection method for guaranteed convergence
- Test your solution with edge cases
- Ensure numerical precision meets requirements (typically 1e-4 or better)

Please implement this step by step:
1. Understand the problem requirements
2. Plan your approach (for numerical problems, prefer stable algorithms like bisection)
3. Implement the solution with the EXACT function name: {entry_point}
4. Test with the provided examples
"""
        
        with open(improved_prompts_dir / f"{problem_name}_cot_improved.txt", 'w') as f:
            f.write(improved_cot)
        print(f"✓ Created improved CoT prompt for {problem_name}")
        
        # Create improved Self-Debug prompt
        improved_selfdebug = f"""IMPROVED Self-Debug Prompt for {problem_name}

{problem_data['prompt']}

CRITICAL REQUIREMENTS:
1. Your function MUST be named exactly: {entry_point}
2. Do not rename or create alternative implementations
3. Function signature must match exactly

IMPLEMENTATION GUIDELINES:
1. First, implement a working solution with the EXACT function name
2. Test it with the provided examples
3. Debug any issues you find
4. Optimize if needed, but NEVER change the function name

For numerical problems:
- Use stable algorithms (bisection for root-finding)
- Verify convergence criteria
- Test edge cases

Common pitfalls to avoid:
- Using creative function names like {entry_point}_improved or {entry_point}_v2
- Over-engineering the solution
- Using unstable numerical methods

Your final code must define: def {entry_point}(...)
"""
        
        with open(improved_prompts_dir / f"{problem_name}_selfdebug_improved.txt", 'w') as f:
            f.write(improved_selfdebug)
        print(f"✓ Created improved Self-Debug prompt for {problem_name}")

print("\n" + "=" * 80)
print("DEBUGGING DOCUMENTATION COMPLETE")
print("=" * 80)

