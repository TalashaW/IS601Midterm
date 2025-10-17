########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


OPERATIONS = {'add', 'subtract', 'multiply', 'divide', 'power', 'root'}


def show_help():
    """Display available commands."""
    print("\nAvailable commands:")
    print("  add, subtract, multiply, divide, power, root - Perform calculations")
    print("  history - Show calculation history")
    print("  clear - Clear calculation history")
    print("  undo - Undo the last calculation")
    print("  redo - Redo the last undone calculation")
    print("  save - Save calculation history to file")
    print("  load - Load calculation history from file")
    print("  exit - Exit the calculator")


def get_user_input(prompt):
    """Get user input with cancel support. Returns None if cancelled."""
    value = input(prompt)
    if value.lower() == 'cancel':
        print("Operation cancelled")
        return None
    return value


def perform_calculation(calc, operation_name):
    """Perform an arithmetic calculation."""
    try:
        print("\nEnter numbers (or 'cancel' to abort):")
        
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

        print(f"\nResult: {result}")
    except (ValidationError, OperationError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def calculator_repl():
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

        print("Calculator started. Type 'help' for commands.")

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()

                if not command:
                    continue

                if command == 'help':
                    show_help()
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print("Goodbye!")
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print("No calculations in history")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    if calc.clear_history():
                        print("History cleared")
                    else:
                        print("No history to clear")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print("Operation undone")
                    else:
                        print("Nothing to undo")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print("Operation redone")
                    else:
                        print("Nothing to redo")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print("History saved successfully")
                    except Exception as e:
                        print(f"Error saving history: {e}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print("History loaded successfully")
                    except Exception as e:
                        print(f"Error loading history: {e}")
                    continue

                if command in OPERATIONS:
                    perform_calculation(calc, command)
                    continue

                # Handle unknown commands
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nOperation cancelled")
                continue
            except EOFError:
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise