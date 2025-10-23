from datasets import load_dataset
import json

# Load dataset
dataset = load_dataset("openai_humaneval")
problems = dataset['test']

selected_ids = [
    'HumanEval/0',   # has_close_elements (Easy)
    'HumanEval/1',   # separate_paren_groups (Easy)
    'HumanEval/31',  # is_prime (Easy)
    'HumanEval/10',  # make_palindrome (Medium)
    'HumanEval/54',  # same_chars (Medium)
    'HumanEval/61',  # correct_bracketing (Medium)
    'HumanEval/108', # count_nums (Medium)
    'HumanEval/32',  # find_zero (Hard)
    'HumanEval/105', # by_length (Hard)
    'HumanEval/163'  # generate_integers (Hard)
]

selected_problems = {}
for problem in problems:
    if problem['task_id'] in selected_ids:
        selected_problems[problem['task_id']] = problem
        
        print(f"\n{'='*70}")
        print(f"Task: {problem['task_id']}")
        print(f"Entry Point: {problem['entry_point']}")
        print(f"{'='*70}")
        print(problem['prompt'])
        print(f"\nCanonical Solution:")
        print(problem['canonical_solution'])
        print(f"\nNumber of tests: {problem['test'].count('assert')}")

# Save to file
with open('selected_humaneval_problems.json', 'w') as f:
    json.dump(selected_problems, f, indent=2)

print(f"\n\nSaved {len(selected_problems)} problems to 'selected_humaneval_problems.json'")