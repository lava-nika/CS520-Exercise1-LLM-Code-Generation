#!/usr/bin/env python3
"""
Comprehensive Analysis for Part 3: TDS Strategy Evaluation
Compares TDS with CoT and Self-Debug strategies
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1")

# Load detailed results
with open(WORKSPACE / "evaluation_results" / "detailed_results.json", 'r') as f:
    results = json.load(f)

# Load pass@k results
with open(WORKSPACE / "evaluation_results" / "pass_at_k_results.json", 'r') as f:
    pass_at_k = json.load(f)

print("=" * 80)
print("PART 3: COMPREHENSIVE ANALYSIS - TDS vs CoT vs Self-Debug")
print("=" * 80)


print("\n" + "=" * 80)
print("STEP 2: QUANTITATIVE EVALUATION RESULTS")
print("=" * 80)

print("\nPASS@K COMPARISON TABLE")
print("-" * 80)

summary_data = []
for model_name in sorted(results.keys()):
    if model_name == "fixed_solutions":
        continue
    for strategy in ['cot', 'selfdebug', 'tds']:
        if strategy in pass_at_k.get(model_name, {}):
            # Keys in pass_at_k are integers, not strings
            p1 = pass_at_k[model_name][strategy].get(1, pass_at_k[model_name][strategy].get('1', 0))
            p2 = pass_at_k[model_name][strategy].get(2, pass_at_k[model_name][strategy].get('2', 0))
            p3 = pass_at_k[model_name][strategy].get(3, pass_at_k[model_name][strategy].get('3', 0))
            summary_data.append({
                'Model': model_name,
                'Strategy': strategy.upper(),
                'Pass@1': f"{p1 * 100:.1f}%",
                'Pass@2': f"{p2 * 100:.1f}%",
                'Pass@3': f"{p3 * 100:.1f}%"
            })

if summary_data:
    df = pd.DataFrame(summary_data)
    print(df.to_string(index=False))

# Detailed failure analysis
print("\n\n🔍 DETAILED FAILURE ANALYSIS")
print("-" * 80)

failures_by_strategy = defaultdict(list)
all_failures = []

for model_name, model_results in results.items():
    if model_name == "fixed_solutions":
        continue
    for problem_name, problem_results in model_results.items():
        for solution_name, solution_result in problem_results.items():
            if not solution_result['success']:
                failure_info = {
                    'model': model_name,
                    'problem': problem_name,
                    'solution': solution_name,
                    'strategy': solution_result['strategy'],
                    'error': solution_result['error'][:150],
                    'file_path': solution_result['file_path']
                }
                failures_by_strategy[solution_result['strategy']].append(failure_info)
                all_failures.append(failure_info)

print(f"\nTotal Failures: {len(all_failures)}")
print("\nFailures by Strategy:")
for strategy in ['cot', 'selfdebug', 'tds']:
    count = len(failures_by_strategy[strategy])
    print(f"  {strategy.upper()}: {count} failures")

# Show TDS failures in detail
if failures_by_strategy['tds']:
    print("\n\nTDS FAILURES (Detailed)")
    print("-" * 80)
    for i, failure in enumerate(failures_by_strategy['tds'], 1):
        print(f"\nTDS Failure {i}:")
        print(f"  Model: {failure['model']}")
        print(f"  Problem: {failure['problem']}")
        print(f"  Solution: {failure['solution']}")
        print(f"  Error: {failure['error']}")
else:
    print("\nNo TDS failures!")


print("\n\n" + "=" * 80)
print("STEP 3: COMPARATIVE ANALYSIS")
print("=" * 80)

# Model-specific analysis
print("\nMODEL-SPECIFIC PERFORMANCE")
print("-" * 80)

model_summary = {}
for model_name in [' claude sonnet4.5', 'gpt5']:
    if model_name not in results:
        continue
    
    model_data = {'strategies': {}}
    for strategy in ['cot', 'selfdebug', 'tds']:
        strategy_data = pass_at_k.get(model_name, {}).get(strategy, {})
        if strategy_data:
            # Keys in pass_at_k are integers
            p1 = strategy_data.get(1, strategy_data.get('1', 0))
            p2 = strategy_data.get(2, strategy_data.get('2', 0))
            p3 = strategy_data.get(3, strategy_data.get('3', 0))
            model_data['strategies'][strategy] = {
                'pass@1': p1,
                'pass@2': p2,
                'pass@3': p3,
                'failures': len([f for f in failures_by_strategy[strategy] if f['model'] == model_name])
            }
    model_summary[model_name] = model_data

for model_name, data in model_summary.items():
    print(f"\n{model_name}:")
    for strategy, metrics in data['strategies'].items():
        print(f"  {strategy.upper()}: Pass@1={metrics['pass@1']*100:.0f}%, "
              f"Pass@2={metrics['pass@2']*100:.0f}%, "
              f"Pass@3={metrics['pass@3']*100:.0f}%, "
              f"Failures={metrics['failures']}")

# Strategy comparison
print("\n\nSTRATEGY COMPARISON ACROSS BOTH MODELS")
print("-" * 80)

strategy_stats = {}
for strategy in ['cot', 'selfdebug', 'tds']:
    total_solutions = 0
    total_failures = 0
    pass_at_1_sum = 0
    count = 0
    
    for model_name in model_summary.keys():
        if strategy in model_summary[model_name]['strategies']:
            metrics = model_summary[model_name]['strategies'][strategy]
            pass_at_1_sum += metrics['pass@1']
            total_failures += metrics['failures']
            count += 1
            total_solutions += 30  
    
    avg_pass_at_1 = pass_at_1_sum / count if count > 0 else 0
    
    strategy_stats[strategy] = {
        'avg_pass@1': avg_pass_at_1,
        'total_failures': total_failures,
        'total_solutions': total_solutions
    }

for strategy, stats in strategy_stats.items():
    print(f"\n{strategy.upper()}:")
    print(f"  Average Pass@1: {stats['avg_pass@1']*100:.1f}%")
    print(f"  Total Failures: {stats['total_failures']}/{stats['total_solutions']}")
    print(f"  Success Rate: {(1 - stats['total_failures']/stats['total_solutions'])*100:.1f}%")

# Error pattern analysis
print("\n\nERROR PATTERN ANALYSIS")
print("-" * 80)

error_patterns = {
    'naming': 0,
    'numerical': 0,
    'logic': 0,
    'other': 0
}

tds_error_patterns = {
    'naming': 0,
    'numerical': 0,
    'logic': 0,
    'other': 0
}

for failure in all_failures:
    error = failure['error'].lower()
    pattern_found = False
    
    if 'nameerror' in error or 'is not defined' in error:
        error_patterns['naming'] += 1
        if failure['strategy'] == 'tds':
            tds_error_patterns['naming'] += 1
        pattern_found = True
    elif 'assertionerror' in error or 'precision' in error or 'fabs' in error:
        error_patterns['numerical'] += 1
        if failure['strategy'] == 'tds':
            tds_error_patterns['numerical'] += 1
        pattern_found = True
    
    if not pattern_found:
        if 'assert' in error:
            error_patterns['logic'] += 1
            if failure['strategy'] == 'tds':
                tds_error_patterns['logic'] += 1
        else:
            error_patterns['other'] += 1
            if failure['strategy'] == 'tds':
                tds_error_patterns['other'] += 1

print("\nAll Strategies - Error Types:")
for pattern, count in error_patterns.items():
    print(f"  {pattern.capitalize()}: {count}")

print("\nTDS Specific - Error Types:")
for pattern, count in tds_error_patterns.items():
    print(f"  {pattern.capitalize()}: {count}")

# Problem-specific analysis
print("\n\nPROBLEM-SPECIFIC ANALYSIS")
print("-" * 80)

problem_failures = defaultdict(lambda: defaultdict(int))
for failure in all_failures:
    problem_failures[failure['problem']][failure['strategy']] += 1

if problem_failures:
    print("\nProblems with failures:")
    for problem, strategies in sorted(problem_failures.items()):
        print(f"\n  {problem}:")
        for strategy, count in strategies.items():
            print(f"    {strategy.upper()}: {count} failures")
else:
    print("\nAll problems passed across all strategies!")

# Key insights
print("\n\nKEY INSIGHTS")
print("-" * 80)

insights = []

# Get metrics for comparison
tds_pass = strategy_stats['tds']['avg_pass@1']
cot_pass = strategy_stats['cot']['avg_pass@1']
tds_failures = strategy_stats['tds']['total_failures']
selfdebug_failures = strategy_stats['selfdebug']['total_failures']
claude_tds = model_summary.get(' claude sonnet4.5', {}).get('strategies', {}).get('tds', {}).get('pass@1', 0)
gpt5_tds = model_summary.get('gpt5', {}).get('strategies', {}).get('tds', {}).get('pass@1', 0)

# Compare TDS to baselines
if tds_pass >= cot_pass and tds_pass >= strategy_stats['selfdebug']['avg_pass@1']:
    insights.append("TDS matches or exceeds both baseline strategies")
elif tds_pass < cot_pass:
    diff = (cot_pass - tds_pass) * 100
    insights.append(f"TDS underperforms CoT by {diff:.1f} percentage points")

if tds_failures == 0:
    insights.append("TDS achieved zero failures - perfect reliability")
elif tds_failures < selfdebug_failures:
    insights.append(f"TDS reduced failures by {selfdebug_failures - tds_failures} compared to Self-Debug")

if tds_error_patterns['naming'] == 0:
    insights.append("TDS successfully eliminated function naming errors (60% of Part 2 failures)")
else:
    insights.append(f"TDS still has {tds_error_patterns['naming']} naming errors")

if tds_error_patterns['numerical'] > 0:
    insights.append(f"TDS has {tds_error_patterns['numerical']} numerical precision errors (needs investigation)")

# Model-specific insights
if claude_tds > gpt5_tds:
    insights.append(f"Claude performs better with TDS ({claude_tds*100:.0f}% vs {gpt5_tds*100:.0f}%)")
elif gpt5_tds > claude_tds:
    insights.append(f"GPT-5 performs better with TDS ({gpt5_tds*100:.0f}% vs {claude_tds*100:.0f}%)")
else:
    insights.append("Both models perform equally well with TDS")

for insight in insights:
    print(f"  {insight}")

# Recommendations
print("\n\nRECOMMENDATIONS")
print("-" * 80)

print("\nWhen to use each strategy:")
print("  • CoT: Best for production code, highest reliability")
print(f"    - Pass@1: {cot_pass*100:.1f}%, Failures: {strategy_stats['cot']['total_failures']}")
print("  • Self-Debug: Good for exploration, but needs constraints")
print(f"    - Pass@1: {strategy_stats['selfdebug']['avg_pass@1']*100:.1f}%, Failures: {strategy_stats['selfdebug']['total_failures']}")
print("  • TDS: ", end="")
if tds_pass >= cot_pass:
    print("Excellent alternative to CoT with built-in verification")
elif tds_pass >= strategy_stats['selfdebug']['avg_pass@1']:
    print("Better than Self-Debug, approaching CoT performance")
else:
    print("Needs refinement for production use")
print(f"    - Pass@1: {tds_pass*100:.1f}%, Failures: {strategy_stats['tds']['total_failures']}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nTotal solutions evaluated: {sum(s['total_solutions'] for s in strategy_stats.values())}")
print(f"Total failures: {len(all_failures)}")
print(f"Overall success rate: {(1 - len(all_failures) / sum(s['total_solutions'] for s in strategy_stats.values())) * 100:.1f}%")
