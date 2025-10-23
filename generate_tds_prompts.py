#!/usr/bin/env python3
"""
Generate Test-Driven Specification (TDS) prompts for all 10 problems
"""

import json
from pathlib import Path

WORKSPACE = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1")

# Load problems
with open(WORKSPACE / "selected_humaneval_problems.json", 'r') as f:
    problems = json.load(f)

# Problem mapping
problem_mapping = {
    "problem1": "HumanEval/0",
    "problem2": "HumanEval/1",
    "problem3": "HumanEval/31",
    "problem4": "HumanEval/10",
    "problem5": "HumanEval/54",
    "problem6": "HumanEval/61",
    "problem7": "HumanEval/108",
    "problem8": "HumanEval/32",
    "problem9": "HumanEval/105",
    "problem10": "HumanEval/163"
}

def create_tds_prompt(problem_key, problem_data):
    """Create a TDS prompt for a given problem"""
    
    entry_point = problem_data['entry_point']
    prompt = problem_data['prompt'].strip()
    
    # Extract examples from docstring if present
    examples = []
    if '>>>' in prompt:
        lines = prompt.split('\n')
        for line in lines:
            if '>>>' in line:
                examples.append(line.strip())
    
    examples_text = "\n".join([f"   {ex}" for ex in examples[:2]]) if examples else "   (See docstring above)"
    
    tds_prompt = f"""Test-Driven Specification (TDS) Prompting Strategy

You will implement a function using a test-driven approach. Follow these three phases carefully:

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: WRITE COMPREHENSIVE TESTS
═══════════════════════════════════════════════════════════════════════════════

Function Specification:
{prompt}

Your Task: Write test cases that thoroughly verify this function.

Requirements:
1. Write at least 6-8 test cases using assert statements
2. CRITICAL: Use the EXACT function name '{entry_point}' in ALL assertions
3. Cover these scenarios:
   - The provided examples above
   - Edge cases (empty inputs, single elements, None values where applicable)
   - Boundary conditions (at limits, just before/after thresholds)
   - Normal cases with various inputs
   - Any special cases mentioned in the docstring

Format your tests as:
    assert {entry_point}(...) == expected_result

Examples from the spec:
{examples_text}

Write your test cases now:

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: IMPLEMENT TO PASS YOUR TESTS
═══════════════════════════════════════════════════════════════════════════════

Now implement the function to pass ALL the tests you just wrote.

Critical Requirements:
✓ Function name MUST be exactly: {entry_point}
✓ Must handle all edge cases from your tests
✓ Consider algorithm efficiency and stability
✓ For numerical problems: use stable algorithms (e.g., bisection for root-finding)
✓ Include proper type hints if shown in the specification

Implementation Guidelines:
- Start simple, then optimize if needed
- Ensure your logic handles all test cases
- For numerical precision: aim for high accuracy (typically 1e-4 or better)
- Don't over-engineer - clarity and correctness first

Provide your implementation:

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: VERIFICATION & REFINEMENT
═══════════════════════════════════════════════════════════════════════════════

Mental Trace-Through:
1. Go through EACH test case you wrote in Phase 1
2. Mentally execute your implementation with those inputs
3. Verify the output matches expected results
4. Check edge cases work correctly

Self-Check Questions:
□ Does my function name exactly match '{entry_point}'?
□ Did I handle all edge cases in my tests?
□ Are there any off-by-one errors?
□ For loops/iterations: am I using correct ranges?
□ For numerical operations: is precision sufficient?
□ Does it work for all input orderings/variations?

If you find any issues during verification, provide the CORRECTED implementation.
Otherwise, confirm your implementation is correct.

═══════════════════════════════════════════════════════════════════════════════
FINAL OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Provide your final, verified implementation below (code only, ready to run):
"""
    
    return tds_prompt

# Generate all TDS prompts
print("=" * 80)
print("GENERATING TEST-DRIVEN SPECIFICATION (TDS) PROMPTS")
print("=" * 80)

prompts_dir = WORKSPACE / "prompts"

for problem_name, humaneval_id in problem_mapping.items():
    problem_data = problems[humaneval_id]
    
    tds_prompt = create_tds_prompt(humaneval_id, problem_data)
    
    output_file = prompts_dir / f"{problem_name}_tds.txt"
    with open(output_file, 'w') as f:
        f.write(tds_prompt)
    
    print(f"✓ Created: {output_file.name}")
    print(f"  Entry point: {problem_data['entry_point']}")
    print(f"  HumanEval ID: {humaneval_id}")
    print()

print("=" * 80)
print("TDS PROMPT GENERATION COMPLETE")
print("=" * 80)
print(f"\nGenerated {len(problem_mapping)} TDS prompt files in: {prompts_dir}")
print("\nNext steps:")
print("  1. Review the generated prompts")
print("  2. Use these prompts with Claude and GPT-5 to generate solutions")
print("  3. Evaluate using the existing evaluation pipeline")
print("  4. Compare TDS results with CoT and Self-Debug")
