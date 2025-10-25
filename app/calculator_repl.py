########################
# Calculator REPL       #
########################
from decimal import Decimal
import logging
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from colorama import Fore, Style, init

OPERATIONS = {'add', 'subtract', 'multiply', 'divide', 
              'power', 'root', 'modulus','intdiv',
              'percentage','absdiff'}

def show_help():
    init(autoreset=True)
    print(Fore.CYAN + "=" * 60)
    """Display available commands."""
    print(Fore.YELLOW + Style.BRIGHT + "\nAvailable commands:")
    print(Fore.GREEN + "\nBasic arithmetic:")
    print("  add -- Addition(a + b)") 
    print("  subtract -- Subtraction (a - b)") 
    print("  multiply -- Multiplication (a × b)") 
    print("  divide -- Division (a / b)") 
    print(Fore.CYAN + "=" * 60) 
    print(Fore.GREEN + "\nAdvanced operations:")
    print("  power -- Exponentiation (a ^ b)")
    print("  root -- Root calculation (ᵇ√a)") 
    print("  modulus -- Modulo operation (a % b)")
    print("  intdiv -- Integer division (a // b)") 
    print("  percentage -- percentage ((a/b) × 100)") 
    print("  absdiff -- Absolute difference (|a - b|)") 
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN +"\nSession management: ")
    print("  history - Show calculation history")
    print("  clear - Clear calculation history")
    print("  undo - Undo the last calculation")
    print("  redo - Redo the last undone calculation")
    print("  save - Save calculation history to file")
    print("  load - Load calculation history from file")
    print("  help - Exit the calculator")
    print("  exit - Exit the calculator")
    print("  ")
    print(Fore.CYAN + "=" * 60)

def get_user_input(prompt):
    """Get user input with cancel support. Returns None if cancelled."""
    value = input(prompt)
    if value.lower() == 'cancel':
        print(Fore.YELLOW + "Operation cancelled")
        return None
    return value

def perform_calculation(calc, operation_name):
    """Perform an arithmetic calculation."""
    try:
        print(Fore.CYAN + "\nEnter numbers (or 'cancel' to abort):")
        
        a = get_user_input("First number: ")
        if a is None:
            return
        
        b = get_user_input("Second number: ")
        if b is None:
            return
        # Create the appropriate operation instance using the Factory pattern
        operation = OperationFactory.create_operation(operation_name)
        calc.set_operation(operation)
        # Perform the calculation
        result = calc.perform_operation(a, b)
        # Normalize the result if it's a Decimal
        if isinstance(result, Decimal):
            result = result.normalize()
        print(Fore.GREEN + Style.BRIGHT + f"\nResult: {result}")
    except (ValidationError, OperationError) as e:
        print(Fore.RED + f"Error: {e}")
        print(Fore.YELLOW + "Tip: Type 'cancel' during input to abort, or 'help' for commands")
    except ValueError as e:
        print(Fore.RED + f"Invalid input: {e}")
        print(Fore.YELLOW + "Please enter valid numbers (e.g., 10, 3.14, -5)")
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {e}")
        logging.error(f"Unexpected error in REPL: {e}", exc_info=True)

def calculator_repl():
    init(autoreset=True)

    """
    Command-line interface for the calculator.
    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()
        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))
        print(Fore.CYAN + "Calculator started. Type 'help' for commands.")
        while True:
            try:
                # Prompt the user for a command
                command = input(Fore.MAGENTA + Style.BRIGHT +"\nEnter command: ").lower().strip()
                if not command:
                    continue
                if command == 'help':
                    show_help()
                    continue
                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(Fore.YELLOW +f"Warning: Could not save history: {e}")
                    print(Fore.CYAN + Style.BRIGHT +"Goodbye!")
                    break
                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue
                if command == 'clear':
                    if calc.clear_history():
                        print(Fore.GREEN + "History cleared")
                    else:
                        print(Fore.YELLOW + "No history to clear")
                    continue
                if command == 'undo':
                    if calc.undo():
                        print(Fore.GREEN + "Operation undone")
                    else:
                        print(Fore.YELLOW + "Nothing to undo")
                    continue
                if command == 'redo':
                    if calc.redo():
                        print(Fore.GREEN + "Operation redone")
                    else:
                        print(Fore.YELLOW + "Nothing to redo")
                    continue
                if command == 'save':
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully")
                    except Exception as e:
                        print(f"Error saving history: {e}")
                    continue
                if command == 'load':
                    try:
                        calc.load_history()
                        print(Fore.GREEN + "History loaded successfully")
                    except Exception as e:
                        print(Fore.RED +f"Error loading history: {e}")
                    continue
                if command in OPERATIONS:
                    perform_calculation(calc, command)
                    continue
                # Handle unknown commands
                print(Fore.YELLOW + f"Unknown command: '{command}'. Type 'help' for available commands.")
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nOperation cancelled")
                continue
            except EOFError:
                print(Fore.YELLOW + "\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
                continue
    except Exception as e:
        # Handle fatal errors during initialization
        print(Fore.RED + f"Fatal error: {e}")
        logging.error(Fore.RED + f"Fatal error in calculator REPL: {e}")
        raise
