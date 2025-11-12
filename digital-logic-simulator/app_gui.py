"""Digital Logic Simulator - GUI Application using Tkinter."""

import sys
import subprocess
import shutil
import os
from pathlib import Path

# Try to import tkinter, with helpful error message and auto-fix if it fails
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError as e:
    if '_tkinter' in str(e) or 'tkinter' in str(e).lower():
        print("=" * 70)
        print("ERROR: Tkinter is not available in this Python installation.")
        print("=" * 70)
        print("\nYour default Python (python3) doesn't have tkinter support.")
        print("This is common with Homebrew Python 3.13+.\n")
        print("SOLUTIONS:")
        print("\n1. Use Python 3.12 (recommended):")
        print("   python3.12 app_gui.py")
        print("\n2. Use system Python:")
        print("   /usr/bin/python3 app_gui.py")
        print("\n3. Use the launcher script:")
        print("   ./run_gui.sh")
        print("   # or")
        print("   python3 run_gui.py")
        print("\n4. Install tkinter for Python 3.13:")
        print("   brew install python-tk@3.13")
        print("\n" + "=" * 70)
        
        # Try to automatically find and run with a working Python
        print("\nAttempting to find a Python with tkinter support...")
        # Prioritize Python 3.12 first (most reliable), then system Python
        python_candidates = [
            ('python3.12', False),
            ('/usr/bin/python3', True),  # System Python - may have macOS version issues
            ('python3.11', False),
            ('python3.10', False),
            ('python3.9', False),
        ]
        
        found_python = None
        for python_cmd, is_absolute in python_candidates:
            python_path = None
            
            if is_absolute:
                # For absolute paths, check if file exists
                if os.path.exists(python_cmd):
                    python_path = python_cmd
            else:
                # For relative paths, use which to find it
                python_path = shutil.which(python_cmd)
            
            if not python_path:
                continue
            
            # Test if this Python has tkinter and can actually run
            try:
                # Test both tkinter import AND that Python can run (no macOS version errors)
                test_code = 'import tkinter; import sys; sys.exit(0)'
                result = subprocess.run(
                    [python_path, '-c', test_code],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                
                # Check if it succeeded AND didn't have stderr errors
                if result.returncode == 0:
                    # Double-check stderr is empty (no warnings that would prevent GUI from working)
                    stderr_text = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ''
                    # Skip if there are critical errors in stderr (like macOS version errors)
                    if 'required' in stderr_text.lower() and 'have instead' in stderr_text.lower():
                        # This is a macOS version error - skip this Python
                        continue
                    found_python = python_path
                    break
            except subprocess.TimeoutExpired:
                # Timeout - skip this Python
                continue
            except (FileNotFoundError, OSError):
                # Python not found or can't execute - skip
                continue
            except Exception:
                # Any other error - skip
                continue
        
        if found_python:
            print(f"✓ Found {found_python} with tkinter support!")
            print(f"  Automatically running with: {found_python}")
            print("\n" + "=" * 70 + "\n")
            # Get the script path
            script_path = os.path.abspath(__file__)
            # Run with the working Python
            try:
                # Use os.execv to replace current process
                os.execv(found_python, [found_python, script_path] + sys.argv[1:])
            except OSError:
                # If execv fails, try subprocess
                try:
                    subprocess.run([found_python, script_path] + sys.argv[1:])
                    sys.exit(0)
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception as run_err:
                    print(f"Error: Could not run with {found_python}: {run_err}")
                    print("Please run manually with one of the solutions above.\n")
                    sys.exit(1)
        else:
            print("\nCould not automatically find a Python with tkinter support.")
            print("Please use one of the manual solutions above.\n")
            sys.exit(1)
    else:
        raise

import re
import itertools
import csv

# Import logic functions for evaluation
from logic import AND, OR, NOT, NAND, NOR, XOR


class DigitalLogicSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Logic Simulator")
        self.root.geometry("900x700")
        
        # State variables
        self.variables = []
        self.variable_toggles = {}  # Dict of variable -> IntVar
        self.current_expression = ""
        self.normalized_expression = ""
        
        # Load last expression if exists
        self.load_last_expression()
        
        # Build GUI
        self.build_gui()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-Return>', lambda e: self.quick_evaluate())
        self.root.bind('<Control-t>', lambda e: self.generate_truth_table())
        self.root.bind('<Control-T>', lambda e: self.generate_truth_table())
        
    def load_last_expression(self):
        """Load last expression from .last_expr file if it exists."""
        try:
            expr_file = Path(".last_expr")
            if expr_file.exists():
                with open(expr_file, 'r') as f:
                    self.last_expression = f.read().strip()
            else:
                self.last_expression = "(A AND B) OR (NOT C)"
        except Exception:
            self.last_expression = "(A AND B) OR (NOT C)"
    
    def save_last_expression(self):
        """Save current expression to .last_expr file."""
        try:
            expr_file = Path(".last_expr")
            with open(expr_file, 'w') as f:
                f.write(self.expression_entry.get())
        except Exception:
            pass  # Silently fail if we can't save
    
    def build_gui(self):
        """Build the GUI components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === Input Panel ===
        input_frame = ttk.LabelFrame(main_frame, text="Input Panel", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Expression label and entry
        ttk.Label(input_frame, text="Boolean Expression:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.expression_entry = ttk.Entry(input_frame, width=50)
        self.expression_entry.insert(0, self.last_expression)
        self.expression_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Detect Variables", 
                  command=self.detect_variables).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Quick Evaluate", 
                  command=self.quick_evaluate).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Generate Truth Table", 
                  command=self.generate_truth_table).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Export CSV...", 
                  command=self.export_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        # === Variables Panel ===
        self.variables_frame = ttk.LabelFrame(main_frame, text="Variables Panel", padding="10")
        self.variables_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # === Results Panel ===
        results_frame = ttk.LabelFrame(main_frame, text="Results Panel", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(results_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create Treeview
        self.tree = ttk.Treeview(tree_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # === Status Bar ===
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def set_status(self, message, ok=True):
        """Set status bar message with color coding."""
        self.status_bar.config(text=message)
        if ok:
            self.status_bar.config(foreground='green')
        else:
            self.status_bar.config(foreground='red')
    
    def tokenize_expression(self, expression):
        """Tokenize expression into variables, operators, and parentheses.
        Returns list of tokens.
        """
        # Pattern to match: variables (A-Z), operators (AND, OR, NOT, NAND, NOR, XOR), parentheses, whitespace
        tokens = []
        i = 0
        operators = ['NAND', 'NOR', 'AND', 'OR', 'NOT', 'XOR']
        
        while i < len(expression):
            # Skip whitespace
            if expression[i].isspace():
                i += 1
                continue
            
            # Check for operators (longest first)
            matched = False
            for op in operators:
                if expression[i:i+len(op)].upper() == op:
                    # Check word boundaries
                    if (i == 0 or not expression[i-1].isalnum()) and \
                       (i+len(op) >= len(expression) or not expression[i+len(op)].isalnum()):
                        tokens.append(op.upper())
                        i += len(op)
                        matched = True
                        break
            
            if matched:
                continue
            
            # Check for parentheses
            if expression[i] in '()':
                tokens.append(expression[i])
                i += 1
                continue
            
            # Check for variable (single uppercase letter)
            if expression[i].isupper() and expression[i].isalpha():
                # Check it's a word boundary (single letter)
                if i+1 >= len(expression) or not expression[i+1].isalnum():
                    tokens.append(expression[i])
                    i += 1
                    continue
            
            # Unknown token
            tokens.append(expression[i])
            i += 1
        
        return tokens
    
    def normalize_expression(self, expression):
        """Normalize expression to Python-safe format using recursive descent parser.
        Converts operators to Python operators (and/or/not/!=) and handles NAND/NOR.
        """
        # First, validate parentheses
        if not self.validate_parentheses(expression):
            raise ValueError("Mismatched parentheses in expression")
        
        # Convert to uppercase and parse recursively
        expr_upper = expression.upper().strip()
        return self._normalize_recursive(expr_upper)
    
    def _normalize_recursive(self, expression):
        """Recursively normalize expression, handling operator precedence."""
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
        
        # Operator precedence (process from lowest to highest):
        # OR, NOR, XOR (lowest precedence, processed first)
        # AND, NAND (higher precedence)
        # NOT (highest precedence, unary, processed last)
        
        # Process OR, NOR, XOR (lowest precedence, left-associative)
        for op in ['OR', 'NOR', 'XOR']:
            depth = 0
            # Find the rightmost occurrence at top level
            for i in range(len(expression) - len(op), -1, -1):
                if expression[i:i+len(op)] == op:
                    # Check word boundaries
                    if (i == 0 or not expression[i-1].isalnum()) and \
                       (i+len(op) >= len(expression) or not expression[i+len(op)].isalnum()):
                        # Check if we're at top level (depth == 0)
                        substr_before = expression[:i]
                        depth_before = substr_before.count('(') - substr_before.count(')')
                        if depth_before == 0:
                            left = expression[:i].strip()
                            right = expression[i+len(op):].strip()
                            left_norm = self._normalize_recursive(left)
                            right_norm = self._normalize_recursive(right)
                            
                            if op == 'OR':
                                return f'({left_norm} or {right_norm})'
                            elif op == 'NOR':
                                return f'not ({left_norm} or {right_norm})'
                            elif op == 'XOR':
                                return f'({left_norm} != {right_norm})'
        
        # Process AND, NAND (higher precedence)
        for op in ['AND', 'NAND']:
            depth = 0
            # Find the rightmost occurrence at top level
            for i in range(len(expression) - len(op), -1, -1):
                if expression[i:i+len(op)] == op:
                    # Check word boundaries
                    if (i == 0 or not expression[i-1].isalnum()) and \
                       (i+len(op) >= len(expression) or not expression[i+len(op)].isalnum()):
                        # Check if we're at top level (depth == 0)
                        substr_before = expression[:i]
                        depth_before = substr_before.count('(') - substr_before.count(')')
                        if depth_before == 0:
                            left = expression[:i].strip()
                            right = expression[i+len(op):].strip()
                            left_norm = self._normalize_recursive(left)
                            right_norm = self._normalize_recursive(right)
                            
                            if op == 'AND':
                                return f'({left_norm} and {right_norm})'
                            elif op == 'NAND':
                                return f'not ({left_norm} and {right_norm})'
        
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
            arg_norm = self._normalize_recursive(arg)
            return f'not {arg_norm}'
        
        # If no operators found, return as-is (should be a variable)
        # Validate it's a single letter variable
        if len(expression) == 1 and expression.isalpha():
            return expression
        elif expression.isalpha():
            raise ValueError(f"Unknown token: {expression}")
        else:
            # Might be an already normalized subexpression, return as-is
            return expression
    
    def validate_parentheses(self, expression):
        """Validate that parentheses are balanced."""
        depth = 0
        for char in expression:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0
    
    def detect_variables(self):
        """Detect variables in the expression and create toggle widgets."""
        expression = self.expression_entry.get().strip()
        if not expression:
            self.set_status("Please enter an expression", ok=False)
            return
        
        try:
            # Validate expression
            if not self.validate_parentheses(expression):
                self.set_status("Error: Mismatched parentheses", ok=False)
                return
            
            # Detect variables using regex (single uppercase letters, excluding operators)
            operators = {'AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR'}
            # Use regex to find single uppercase letters that are word boundaries
            expr_upper = expression.upper()
            # Find all single letter variables using word boundaries
            potential_vars = re.findall(r'\b[A-Z]\b', expr_upper)
            # Filter out operators
            variables = sorted(set([v for v in potential_vars if v not in operators]))
            
            # Also validate by trying to normalize
            try:
                test_normalized = self.normalize_expression(expression)
                # Check for unknown tokens in normalized expression
                # If normalization succeeds, variables are valid
            except ValueError as e:
                error_msg = str(e)
                if "Unknown token" in error_msg:
                    self.set_status(f"Error: {error_msg}", ok=False)
                    return
                elif "Mismatched parentheses" in error_msg:
                    self.set_status("Error: Mismatched parentheses", ok=False)
                    return
                else:
                    raise
            
            if not variables:
                self.set_status("No variables detected in expression", ok=False)
                return
            
            self.variables = variables
            self.current_expression = expression
            
            # Normalize expression
            try:
                self.normalized_expression = self.normalize_expression(expression)
            except Exception as e:
                self.set_status(f"Error normalizing expression: {str(e)}", ok=False)
                return
            
            # Clear existing variable toggles
            for widget in self.variables_frame.winfo_children():
                widget.destroy()
            self.variable_toggles = {}
            
            # Create toggle widgets
            ttk.Label(self.variables_frame, text="Variable Values (0/1):").pack(anchor=tk.W, pady=(0, 5))
            toggles_frame = ttk.Frame(self.variables_frame)
            toggles_frame.pack(fill=tk.X)
            
            for var in variables:
                var_frame = ttk.Frame(toggles_frame)
                var_frame.pack(side=tk.LEFT, padx=10)
                ttk.Label(var_frame, text=f"{var}:").pack(side=tk.LEFT, padx=(0, 5))
                var_intvar = tk.IntVar(value=0)
                self.variable_toggles[var] = var_intvar
                ttk.Checkbutton(var_frame, variable=var_intvar, 
                               command=lambda v=var: self.update_toggle_label(v)).pack(side=tk.LEFT)
                self.toggle_labels = getattr(self, 'toggle_labels', {})
                self.toggle_labels[var] = ttk.Label(var_frame, text="0")
                self.toggle_labels[var].pack(side=tk.LEFT, padx=(5, 0))
            
            self.set_status(f"Detected {len(variables)} variable(s): {', '.join(variables)}", ok=True)
            self.save_last_expression()
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}", ok=False)
    
    def update_toggle_label(self, var):
        """Update the label next to a toggle button."""
        value = self.variable_toggles[var].get()
        if hasattr(self, 'toggle_labels') and var in self.toggle_labels:
            self.toggle_labels[var].config(text=str(value))
    
    def evaluate_expression_safe(self, variable_values):
        """Safely evaluate the normalized expression with given variable values."""
        if not self.normalized_expression:
            raise ValueError("No expression to evaluate. Please detect variables first.")
        
        # Create a safe namespace
        # Convert variable values to Python booleans
        namespace = {var: bool(val) for var, val in variable_values.items()}
        namespace['True'] = True
        namespace['False'] = False
        
        # Evaluate the expression
        try:
            result = eval(self.normalized_expression, {"__builtins__": {}}, namespace)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Evaluation error: {str(e)}")
    
    def quick_evaluate(self):
        """Quickly evaluate expression with current toggle values."""
        if not self.variables:
            self.set_status("Please detect variables first", ok=False)
            return
        
        try:
            # Get current toggle values
            variable_values = {var: self.variable_toggles[var].get() 
                             for var in self.variables}
            
            # Evaluate
            result = self.evaluate_expression_safe(variable_values)
            
            # Clear table and show single row
            self.clear_table()
            self.setup_table_columns()
            
            # Configure tag colors (apply before inserting)
            self.tree.tag_configure('result_1', background='#90EE90')  # Bright light green
            self.tree.tag_configure('result_0', background='#FFB6C1')  # Bright light pink
            
            # Add the single row
            row_values = [variable_values[var] for var in self.variables] + [int(result)]
            self.tree.insert('', 'end', values=row_values, tags=('result_1' if result else 'result_0',))
            
            self.set_status(f"Quick evaluate: Output = {int(result)}", ok=True)
            self.save_last_expression()
            
        except Exception as e:
            self.set_status(f"Evaluation error: {str(e)}", ok=False)
    
    def generate_truth_table(self):
        """Generate full truth table for all input combinations."""
        if not self.variables:
            self.set_status("Please detect variables first", ok=False)
            return
        
        try:
            # Clear table
            self.clear_table()
            self.setup_table_columns()
            
            # Configure tag colors - brighter colors for better visibility (do this before inserting rows)
            self.tree.tag_configure('result_1', background='#90EE90')  # Bright light green
            self.tree.tag_configure('result_0', background='#FFB6C1')  # Bright light pink
            
            # Generate all combinations
            combinations = list(itertools.product([0, 1], repeat=len(self.variables)))
            
            # Evaluate each combination
            for combo in combinations:
                variable_values = {var: val for var, val in zip(self.variables, combo)}
                result = self.evaluate_expression_safe(variable_values)
                
                row_values = list(combo) + [int(result)]
                tag = 'result_1' if result else 'result_0'
                self.tree.insert('', 'end', values=row_values, tags=(tag,))
            
            self.set_status(f"Generated truth table with {len(combinations)} rows", ok=True)
            self.save_last_expression()
            
        except Exception as e:
            self.set_status(f"Error generating truth table: {str(e)}", ok=False)
    
    def setup_table_columns(self):
        """Setup table columns based on current variables."""
        # Clear existing columns
        self.tree['columns'] = self.variables + ['Output']
        self.tree['show'] = 'headings'
        
        # Configure columns
        for col in self.variables + ['Output']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
    
    def clear_table(self):
        """Clear all rows from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def export_csv(self):
        """Export truth table to CSV file."""
        if not self.variables:
            self.set_status("No data to export", ok=False)
            return
        
        # Get table data
        items = self.tree.get_children()
        if not items:
            self.set_status("No data to export. Generate truth table first.", ok=False)
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Truth Table as CSV"
        )
        
        if not filename:
            return
        
        try:
            # Write CSV
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(self.variables + ['Output'])
                
                # Write rows
                for item in items:
                    values = self.tree.item(item, 'values')
                    writer.writerow(values)
            
            self.set_status(f"Exported to: {os.path.basename(filename)}", ok=True)
            
        except Exception as e:
            self.set_status(f"Export error: {str(e)}", ok=False)
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = DigitalLogicSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

