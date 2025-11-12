"""Digital Logic Simulator - Boolean expression evaluator and truth table generator."""

import re
import itertools
from logic import AND, OR, NOT, NAND, NOR, XOR

def detect_variables(expression):
    """Extract all variable names from the expression (single uppercase letters)."""
    # Find all single uppercase letters that are variables
    variables = sorted(set(re.findall(r'\b[A-Z]\b', expression)))
    return variables

def convert_to_function_calls(expression):
    """Convert infix notation (A AND B) to function calls (AND(A, B)).
    
    Uses a recursive descent parser that handles operator precedence:
    - NOT (highest precedence, unary)
    - AND, NAND (binary)
    - OR, NOR, XOR (lowest precedence, binary)
    """
    expression = expression.strip()
    
    # Remove outer parentheses if the entire expression is wrapped
    depth = 0
    can_remove = True
    for i, char in enumerate(expression):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0 and i < len(expression) - 1:
                can_remove = False
                break
    if can_remove and expression.startswith('(') and expression.endswith(')'):
        expression = expression[1:-1].strip()
    
    # Operator precedence (process from lowest to highest)
    # OR, NOR, XOR have lowest precedence (processed first)
    # AND, NAND have higher precedence
    # NOT has highest precedence (processed last, but handled separately)
    
    # Process OR, NOR, XOR (lowest precedence, left-associative)
    for op in ['OR', 'NOR', 'XOR']:
        depth = 0
        # Find the rightmost occurrence at top level
        for i in range(len(expression) - len(op), -1, -1):
            if expression[i:i+len(op)] == op:
                # Check if we're at word boundaries and top level
                if (i == 0 or not expression[i-1].isalnum()) and \
                   (i+len(op) >= len(expression) or not expression[i+len(op)].isalnum()):
                    # Check if we're at top level (depth == 0)
                    substr_before = expression[:i]
                    depth_before = substr_before.count('(') - substr_before.count(')')
                    if depth_before == 0:
                        left = expression[:i].strip()
                        right = expression[i+len(op):].strip()
                        left_conv = convert_to_function_calls(left)
                        right_conv = convert_to_function_calls(right)
                        return f'{op}({left_conv}, {right_conv})'
    
    # Process AND, NAND (higher precedence)
    for op in ['AND', 'NAND']:
        depth = 0
        # Find the rightmost occurrence at top level
        for i in range(len(expression) - len(op), -1, -1):
            if expression[i:i+len(op)] == op:
                # Check if we're at word boundaries and top level
                if (i == 0 or not expression[i-1].isalnum()) and \
                   (i+len(op) >= len(expression) or not expression[i+len(op)].isalnum()):
                    # Check if we're at top level (depth == 0)
                    substr_before = expression[:i]
                    depth_before = substr_before.count('(') - substr_before.count(')')
                    if depth_before == 0:
                        left = expression[:i].strip()
                        right = expression[i+len(op):].strip()
                        left_conv = convert_to_function_calls(left)
                        right_conv = convert_to_function_calls(right)
                        return f'{op}({left_conv}, {right_conv})'
    
    # Process NOT (unary, highest precedence)
    if expression.startswith('NOT '):
        arg = expression[4:].strip()
        # Remove parentheses if the entire argument is wrapped
        if arg.startswith('(') and arg.endswith(')'):
            depth = 0
            can_remove = True
            for i, char in enumerate(arg):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0 and i < len(arg) - 1:
                        can_remove = False
                        break
            if can_remove:
                arg = arg[1:-1].strip()
        arg_conv = convert_to_function_calls(arg)
        return f'NOT({arg_conv})'
    
    # If no operators found, return as-is (should be a variable)
    return expression

def evaluate_expression(expression, variable_values):
    """Evaluate the Boolean expression with given variable values."""
    # Convert infix notation to function calls
    converted_expr = convert_to_function_calls(expression)
    
    # Create a safe namespace with only the gate functions and variable values
    namespace = {
        'AND': AND,
        'OR': OR,
        'NOT': NOT,
        'NAND': NAND,
        'NOR': NOR,
        'XOR': XOR,
        **variable_values
    }
    
    # Evaluate the expression safely
    try:
        result = eval(converted_expr, {"__builtins__": {}}, namespace)
        return bool(result)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}. Converted expression: {converted_expr}")

def generate_truth_table(expression):
    """Generate and print a truth table for the given Boolean expression."""
    # Detect variables
    variables = detect_variables(expression)
    
    if not variables:
        print("No variables found in the expression.")
        return
    
    # Generate all possible combinations of True/False for the variables
    combinations = list(itertools.product([False, True], repeat=len(variables)))
    
    # Calculate column widths
    col_width = max(8, max(len(var) for var in variables) + 2)
    result_width = max(10, len(expression) + 2)
    
    # Print header
    header = " | ".join(f"{var:^{col_width}}" for var in variables)
    header += f" | {expression:^{result_width}}"
    print(header)
    print("-" * len(header))
    
    # Print each row
    for combo in combinations:
        # Create dictionary mapping variables to their values
        var_dict = {var: val for var, val in zip(variables, combo)}
        
        # Evaluate expression
        result = evaluate_expression(expression, var_dict)
        
        # Print row
        row = " | ".join(f"{str(val):^{col_width}}" for val in combo)
        row += f" | {str(result):^{result_width}}"
        print(row)

def main():
    """Main function to run the digital logic simulator."""
    print("=" * 60)
    print("Digital Logic Simulator")
    print("=" * 60)
    print("\nEnter a Boolean expression using:")
    print("  - Variables: Single uppercase letters (A, B, C, ...)")
    print("  - Gates: AND, OR, NOT, NAND, NOR, XOR")
    print("  - Example: (A AND B) OR (NOT C)")
    print("\nType 'quit' to exit.\n")
    
    while True:
        expression = input("Enter expression: ").strip()
        
        if expression.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not expression:
            print("Please enter a valid expression.")
            continue
        
        try:
            print("\nTruth Table:")
            print("-" * 60)
            generate_truth_table(expression)
            print()
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()

