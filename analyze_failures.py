#!/usr/bin/env python3
"""
Analysis Script for Part 2: Debugging & Iterative Improvement
This script identifies failure cases and provides detailed analysis for debugging.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def analyze_failures():
    """Analyze failure cases to identify debugging opportunities."""
    
    # Load detailed results
    results_file = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1/evaluation_results/detailed_results.json")
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    failures = []
    
    # Find all failure cases
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
    print("FAILURE ANALYSIS FOR PART 2: DEBUGGING & ITERATIVE IMPROVEMENT")
    print("=" * 80)
    print(f"\nTotal failures found: {len(failures)}")
    
    if len(failures) == 0:
        print("\n🎉 Excellent! No failures found in the current evaluation.")
        print("Since the assignment requires at least 2 failure cases for Part 2:")
        print("1. You may need to add more challenging problems")
        print("2. Or examine edge cases that might cause failures")
        print("3. Consider testing with different prompting strategies")
        return
    
    # Group failures by model and strategy
    print("\n" + "=" * 50)
    print("FAILURE BREAKDOWN BY MODEL AND STRATEGY")
    print("=" * 50)
    
    failure_df = pd.DataFrame(failures)
    if not failure_df.empty:
        breakdown = failure_df.groupby(['model', 'strategy']).size().reset_index(name='failure_count')
        print(breakdown.to_string(index=False))
    
    print("\n" + "=" * 50)
    print("DETAILED FAILURE CASES")
    print("=" * 50)
    
    for i, failure in enumerate(failures, 1):
        print(f"\n--- Failure Case {i} ---")
        print(f"Model: {failure['model']}")
        print(f"Strategy: {failure['strategy']}")
        print(f"Problem: {failure['problem']}")
        print(f"Solution File: {failure['solution']}")
        print(f"Error: {failure['error'][:200]}{'...' if len(failure['error']) > 200 else ''}")
        print(f"Full File Path: {failure['file_path']}")
        
        # Read the actual code that failed
        try:
            with open(failure['file_path'], 'r') as f:
                code = f.read()
            print("\nFailed Code:")
            print("-" * 30)
            print(code)
            print("-" * 30)
        except Exception as e:
            print(f"Could not read code file: {e}")
    
    # Recommendations for Part 2
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS FOR PART 2 ANALYSIS")
    print("=" * 50)
    
    print("\n1. For each failure case, analyze:")
    print("   - What specific test case caused the failure")
    print("   - Whether it's a logic error, syntax error, or edge case handling")
    print("   - How the error differs between models/strategies")
    
    print("\n2. Debug the failures by:")
    print("   - Running the failing code manually with test inputs")
    print("   - Identifying the root cause (reasoning gap, poor error handling, etc.)")
    print("   - Comparing working vs failing solutions")
    
    print("\n3. Iterative improvement strategies:")
    print("   - Refine prompts with more specific debugging hints")
    print("   - Add examples of edge case handling")
    print("   - Use self-correction prompting techniques")
    
    print("\n4. Compare model effectiveness:")
    print("   - Which model struggles more with which types of problems?")
    print("   - Are certain strategies more prone to specific error types?")
    print("   - How does debugging effectiveness differ between models?")
    
    return failures

def create_debugging_template():
    """Create a template for documenting debugging process."""
    
    template = """
# Debugging Analysis Template for Part 2

## Failure Case Analysis

### Case 1: [Failure Description]
- **Model**: [Model Name]
- **Strategy**: [CoT/Self-Debug]
- **Problem**: [Problem ID and Description]
- **Error Type**: [Syntax/Logic/Edge Case/etc.]

#### Root Cause Analysis:
1. **What went wrong**: 
2. **Why it happened**: 
3. **Test case that triggered failure**: 

#### Debugging Steps Taken:
1. 
2. 
3. 

#### Solution/Improvement:
- **Modified Prompt**: 
- **Additional Hints Provided**: 
- **Result**: 

---

### Case 2: [Failure Description]
[Repeat structure above]

## Cross-Model Comparison

### Model Performance Differences:
- **Claude vs GPT5**: 
- **Strategy Effectiveness**: 
- **Error Pattern Differences**: 

### Debugging Effectiveness:
- **Which debugging approaches worked best**: 
- **Model-specific debugging requirements**: 
- **Strategy-specific improvements needed**: 

## Recommendations for Future Improvements:
1. 
2. 
3. 
"""
    
    output_file = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1/evaluation_results/debugging_template.md")
    with open(output_file, 'w') as f:
        f.write(template)
    
    print(f"\nDebugging template created: {output_file}")

if __name__ == "__main__":
    failures = analyze_failures()
    create_debugging_template()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS FOR YOUR ASSIGNMENT")
    print("=" * 80)
    print("\nPart 1 Complete: Pass@k metrics calculated successfully")
    print("Results saved in evaluation_results/ directory")
    print("Use the debugging_template.md to document your Part 2 analysis")
    print("\nFor Part 2, focus on the failure cases identified above")
    print("Implement debugging improvements and re-run evaluation")