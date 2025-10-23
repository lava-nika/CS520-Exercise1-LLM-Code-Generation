#!/usr/bin/env python3
"""
Pass@k Metric Calculation for HumanEval Code Generation
This script evaluates generated code solutions and calculates pass@k metrics.
"""

import json
import os
import sys
import subprocess
import tempfile
import traceback
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import pandas as pd
from pathlib import Path

class PassAtKEvaluator:
    def __init__(self, workspace_path: str):
        """
        Initialize the evaluator with the workspace path.
        
        Args:
            workspace_path: Path to the exercise workspace
        """
        self.workspace_path = Path(workspace_path)
        self.problems_file = self.workspace_path / "selected_humaneval_problems.json"
        self.generated_code_dir = self.workspace_path / "generated code"
        self.results = defaultdict(lambda: defaultdict(dict))
        
        # Load the problems and test cases
        with open(self.problems_file, 'r') as f:
            self.problems = json.load(f)
            
        # Problem mapping (based on the file structure)
        self.problem_mapping = {
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
    
    def execute_solution(self, solution_code: str, problem_key: str) -> Tuple[bool, str]:
        """
        Execute a solution against the test cases for a given problem.
        
        Args:
            solution_code: The Python code to test
            problem_key: Key identifying the problem (e.g., "HumanEval/0")
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            # Get the test cases for this problem
            problem_data = self.problems[problem_key]
            test_code = problem_data['test']
            
            # Create a temporary file with the solution and test
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Write the solution code
                f.write(solution_code)
                f.write('\n\n')
                # Write the test code
                f.write(test_code)
                f.write('\n\n')
                # Add execution code
                f.write('if __name__ == "__main__":\n')
                f.write(f'    check({problem_data["entry_point"]})\n')
                f.write('    print("All tests passed!")\n')
                
                temp_file = f.name
            
            # Execute the file
            result = subprocess.run(
                [sys.executable, temp_file], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, "Success"
            else:
                return False, result.stderr or result.stdout
                
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def evaluate_all_solutions(self):
        """Evaluate all generated solutions and store results."""
        print("Evaluating all generated solutions...")
        
        # Iterate through all model directories
        for model_dir in self.generated_code_dir.iterdir():
            if not model_dir.is_dir():
                continue
                
            model_name = model_dir.name
            print(f"\nEvaluating model: {model_name}")
            
            # Iterate through all problem directories
            for problem_dir in model_dir.iterdir():
                if not problem_dir.is_dir():
                    continue
                    
                problem_name = problem_dir.name
                problem_key = self.problem_mapping.get(problem_name)
                
                if not problem_key:
                    print(f"Warning: Unknown problem {problem_name}")
                    continue
                
                print(f"  Evaluating {problem_name} ({problem_key})")
                
                # Evaluate all solution files in this problem directory
                solution_files = list(problem_dir.glob("*.py"))
                for solution_file in solution_files:
                    try:
                        with open(solution_file, 'r') as f:
                            solution_code = f.read()
                        
                        success, error = self.execute_solution(solution_code, problem_key)
                        
                        # Extract strategy and sample info from filename
                        filename = solution_file.stem
                        if 'cot' in filename:
                            strategy = 'cot'
                        elif 'selfdebug' in filename:
                            strategy = 'selfdebug'
                        elif 'tds' in filename:
                            strategy = 'tds'
                        else:
                            strategy = 'unknown'
                        
                        # Store result
                        self.results[model_name][problem_name][filename] = {
                            'success': success,
                            'error': error,
                            'strategy': strategy,
                            'file_path': str(solution_file)
                        }
                        
                        status = "✓" if success else "✗"
                        print(f"    {status} {solution_file.name}")
                        
                    except Exception as e:
                        print(f"    ✗ {solution_file.name} - Error reading file: {e}")
    
    def calculate_pass_at_k(self, k_values: List[int] = [1, 2, 3]) -> Dict[str, Dict[str, Dict[int, float]]]:
        """
        Calculate pass@k metrics for different values of k.
        
        Args:
            k_values: List of k values to calculate metrics for
            
        Returns:
            Dictionary with pass@k results organized by model, strategy, and k value
        """
        pass_at_k_results = defaultdict(lambda: defaultdict(dict))
        
        for model_name, model_results in self.results.items():
            # Group results by strategy
            strategy_results = defaultdict(lambda: defaultdict(list))
            
            for problem_name, problem_results in model_results.items():
                for solution_name, solution_result in problem_results.items():
                    strategy = solution_result['strategy']
                    strategy_results[strategy][problem_name].append(solution_result['success'])
            
            # Calculate pass@k for each strategy
            for strategy, strategy_data in strategy_results.items():
                for k in k_values:
                    if k <= 3:  # We only have 3 samples per strategy
                        total_problems = len(strategy_data)
                        problems_with_at_least_one_success = 0
                        
                        for problem_name, successes in strategy_data.items():
                            # Take first k samples
                            k_samples = successes[:k]
                            if any(k_samples):
                                problems_with_at_least_one_success += 1
                        
                        pass_at_k = problems_with_at_least_one_success / total_problems if total_problems > 0 else 0
                        pass_at_k_results[model_name][strategy][k] = pass_at_k
        
        return pass_at_k_results
    
    def generate_detailed_report(self, pass_at_k_results: Dict) -> str:
        """Generate a detailed report with all results."""
        report = []
        report.append("=" * 80)
        report.append("PASS@K EVALUATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary table
        report.append("PASS@K SUMMARY")
        report.append("-" * 40)
        
        # Create summary DataFrame
        summary_data = []
        for model_name, model_data in pass_at_k_results.items():
            for strategy, strategy_data in model_data.items():
                row = {
                    'Model': model_name,
                    'Strategy': strategy,
                    'Pass@1': f"{strategy_data.get(1, 0):.2%}",
                    'Pass@2': f"{strategy_data.get(2, 0):.2%}",
                    'Pass@3': f"{strategy_data.get(3, 0):.2%}"
                }
                summary_data.append(row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            report.append(df.to_string(index=False))
        report.append("")
        
        # Detailed results by problem
        report.append("DETAILED RESULTS BY PROBLEM")
        report.append("-" * 40)
        
        for model_name, model_results in self.results.items():
            report.append(f"\nModel: {model_name}")
            report.append("-" * 30)
            
            for problem_name, problem_results in model_results.items():
                problem_key = self.problem_mapping.get(problem_name, "Unknown")
                report.append(f"\n  {problem_name} ({problem_key})")
                
                # Group by strategy
                cot_results = []
                selfdebug_results = []
                
                for solution_name, solution_result in problem_results.items():
                    status = "✓" if solution_result['success'] else "✗"
                    result_str = f"    {status} {solution_name}"
                    if not solution_result['success'] and solution_result['error']:
                        # Truncate long error messages
                        error = solution_result['error'][:100] + "..." if len(solution_result['error']) > 100 else solution_result['error']
                        result_str += f" ({error})"
                    
                    if solution_result['strategy'] == 'cot':
                        cot_results.append(result_str)
                    elif solution_result['strategy'] == 'selfdebug':
                        selfdebug_results.append(result_str)
                
                if cot_results:
                    report.append("    Chain-of-Thought:")
                    report.extend(cot_results)
                
                if selfdebug_results:
                    report.append("    Self-Debug:")
                    report.extend(selfdebug_results)
        
        return "\n".join(report)
    
    def save_results(self, output_dir: str = None):
        """Save results to files."""
        if output_dir is None:
            output_dir = self.workspace_path / "evaluation_results"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # Calculate pass@k results
        pass_at_k_results = self.calculate_pass_at_k()
        
        # Save detailed results as JSON
        with open(output_dir / "detailed_results.json", 'w') as f:
            json.dump(dict(self.results), f, indent=2)
        
        # Save pass@k results as JSON
        with open(output_dir / "pass_at_k_results.json", 'w') as f:
            json.dump(dict(pass_at_k_results), f, indent=2)
        
        # Generate and save report
        report = self.generate_detailed_report(pass_at_k_results)
        with open(output_dir / "evaluation_report.txt", 'w') as f:
            f.write(report)
        
        # Save summary CSV
        summary_data = []
        for model_name, model_data in pass_at_k_results.items():
            for strategy, strategy_data in model_data.items():
                row = {
                    'Model': model_name,
                    'Strategy': strategy,
                    'Pass@1': strategy_data.get(1, 0),
                    'Pass@2': strategy_data.get(2, 0),
                    'Pass@3': strategy_data.get(3, 0)
                }
                summary_data.append(row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(output_dir / "pass_at_k_summary.csv", index=False)
        
        print(f"\nResults saved to: {output_dir}")
        print(f"Files created:")
        print(f"  - detailed_results.json")
        print(f"  - pass_at_k_results.json") 
        print(f"  - evaluation_report.txt")
        print(f"  - pass_at_k_summary.csv")
        
        return pass_at_k_results

def main():
    """Main function to run the evaluation."""
    workspace_path = "/Users/lavanika/Desktop/Fall 2025/520/assignments/Ex1"
    
    # Initialize evaluator
    evaluator = PassAtKEvaluator(workspace_path)
    
    # Evaluate all solutions
    evaluator.evaluate_all_solutions()
    
    # Calculate and save results
    pass_at_k_results = evaluator.save_results()
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    for model_name, model_data in pass_at_k_results.items():
        print(f"\n{model_name}:")
        for strategy, strategy_data in model_data.items():
            print(f"  {strategy.upper()}:")
            for k, score in strategy_data.items():
                print(f"    Pass@{k}: {score:.2%}")

if __name__ == "__main__":
    main()