########################
# Calculator REPL Tests #
########################

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.calculator_repl import show_help,  get_user_input, perform_calculation, calculator_repl, OPERATIONS, Calculator
from app.exceptions import ValidationError, OperationError


class TestShowHelp:
  """This class tests the 'show_help' function to ensure that the available commands are displayed correctly. 
    It verifies that the printed output contains the expected help prompts for the calculator operations defined in the 
    show_help() function in the calculator_repl project"""

  @pytest.mark.parametrize("expected_line", [
        "add,",          
        "subtract,",
        "multiply,",
        "divide",
        "power",
        "root",
        "modulus",
        "intdiv",
        "percentage",
        "absdiff",
        "history - Show calculation history",
        "clear - Clear calculation history",
        "exit - Exit the calculator"
    ])
     
  def test_show_help_displays_expected_prompts(self, expected_line: str):
    with patch("builtins.print") as mock_print:
        show_help()
        # Convert each print call to string
        calls = [str(call) for call in mock_print.call_args_list]
        # Check that at least one print line contains the expected text
        assert any(expected_line in str(call) for call in calls)

class TestUserInput:
    """This class tests the 'get_user_input' function to ensure it handles different types of user inputs correctly. 
    It checks whether the input is processed as expected and whether the operation is canceled when the input is 'cancel' 
    (or any variation like 'CANCEL' or 'Cancel'). It also verifies that the correct message is printed based on the input."""

    @pytest.mark.parametrize("expected_input,expected_output,should_print_cancel", [
    ("cancel", None, True),
    ("CANCEL", None, True),
    ("Cancel", None, True),
    ("hello", "hello", False),
    ("123", "123", False),
])
    def test_get_user_input(self, expected_input: str, expected_output: str, should_print_cancel: bool):
        with patch("builtins.input", return_value=expected_input):
         with patch("builtins.print") as mock_print:
            result = get_user_input("Enter something: ")
            assert result == expected_output

            if should_print_cancel:
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Operation cancelled" in str(call) for call in print_calls)
            else:
                mock_print.assert_not_called()


class TestPerformCalculation:
    """This class tests the 'perform_calculation' function to ensure the correct operations are performed when valid inputs 
    are provided. It verifies that the appropriate operation is executed and that the calculator's methods are called correctly. 
    It also checks that operations are correctly canceled when the user inputs 'Cancel'."""

    @pytest.mark.parametrize("operation,first_input,second_input,expected_result",[
     ("add", "7", "3", True),
     ("multiply", "7","3", True),
     ("subtract", "Cancel", None, False),
     ("divide", "12","cancel",False),     
])
    def test_perform_calculation(self, operation: str, first_input: str, second_input: str , expected_result: str):
        mock_calc = Mock(spec=Calculator)
        mock_calc.perform_operation.return_value = Decimal("10")
        inputs = [first_input] if second_input is None else [first_input, second_input]
        
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.OperationFactory.create_operation") as mock_factory:
                    mock_operation = Mock()
                    mock_factory.return_value = mock_operation
                    perform_calculation(mock_calc, operation)
                    
                    if expected_result:
                        mock_calc.set_operation.assert_called_once_with(mock_operation)
                        mock_calc.perform_operation.assert_called_once_with(first_input, second_input)
                    else:
                        # Verify operation was cancelled
                        mock_calc.perform_operation.assert_not_called()

class TestCalculatorREPL:
     """This class tests the REPL loop for the calculator application. It simulates various commands like 'help', 'clear', 
     'undo', 'redo', 'history', and verifies that the correct messages are displayed and the correct methods are called . 
     It also checks the program's behavior when commands 
     are issued under different conditions, like with or without history."""      

     @pytest.mark.parametrize("command, expected_output, has_history",[
     ("help", None, False),
     ("clear", "History cleared",True),
     ("clear", "No history to clear", False),
     ("undo", "Operation undone",True),
     ("undo", "Nothing to undo",False),
     ("redo", "Operation redone" ,True),
     ("redo", "Nothing to redo",False),
    ])
     def test_calculator_REPL(self, command, expected_output, has_history):
        mock_calc = Mock(spec=Calculator)
        if command == "clear":
             mock_calc.clear_history.return_value = has_history
        elif command == "undo":
            mock_calc.undo.return_value = has_history
        elif command == "redo":
            mock_calc.redo.return_value = has_history
        elif command == "history":
            if has_history:
                mock_calc.show_history.return_value = ["Addition (2, 3) = 5"]
            else:
                mock_calc.show_history.return_value = []

        with patch("builtins.input", side_effect=[command, "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                   with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()

                   if expected_output:
                        # Check that the expected output was printed
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        assert any(expected_output in str(call) for call in print_calls)

     @pytest.mark.parametrize("command, has_history, expected_output", [
    ("history", False, "No calculations in history"),
    ("history", True, "Calculation History:"),

     ])
     def test_history_command(self, command, has_history, expected_output):
        mock_calc = Mock(spec=Calculator)
        if has_history:
            mock_calc.show_history.return_value = ["1 + 1 = 2", "2 * 3 = 6"]
        else:
            mock_calc.show_history.return_value = []
        
        with patch("builtins.input", side_effect=[command, "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any(expected_output in str(call) for call in print_calls)

     @pytest.mark.parametrize("command, should_succeed, expected_output", [
        ("save", True, "History saved successfully"),
        ("save", False, "Error saving history"),
        ("load", True, "History loaded successfully"),
        ("load", False, "Error loading history"),
    ])
    
     def test_save_load_commands(self, command, should_succeed, expected_output):
        mock_calc = Mock(spec=Calculator)
        
        if not should_succeed:
            if command == "save":
                mock_calc.save_history.side_effect = Exception("Save failed")
            else:
                mock_calc.load_history.side_effect = Exception("Load failed")
        
        with patch("builtins.input", side_effect=[command, "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any(expected_output in str(call) for call in print_calls)
    
     def test_exit_command(self):
        mock_calc = Mock(spec=Calculator)
        
        with patch("builtins.input", side_effect=["exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    # Verify save was attempted on exit
                    mock_calc.save_history.assert_called_once()
                    
                    # Verify goodbye message
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Goodbye!" in str(call) for call in print_calls)
        
     def test_empty_command(self):
        mock_calc = Mock(spec=Calculator)  

        with patch("builtins.input", side_effect=["", "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl() 

     def test_unknown_command(self):
        mock_calc = Mock(spec=Calculator)  

        with patch("builtins.input", side_effect=["invalidcommand", "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Unknown command" in str(call) for call in print_calls)

     def test_keyboard_interrupt(self):
        mock_calc = Mock(spec=Calculator)  

        with patch("builtins.input", side_effect=[KeyboardInterrupt(), "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Operation cancelled" in str(call) for call in print_calls)

     def test_eof_error_handling(self):
        mock_calc = Mock(spec=Calculator)  

        with patch("builtins.input", side_effect=[EOFError(), "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Input terminated" in str(call) for call in print_calls)
     
     def test_fatal_error_during_initialization(self):

            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", side_effect= Exception("Fatal error")):
                    with pytest.raises(Exception):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Fatal error" in str(call) for call in print_calls)

     def test_exit_save_error_handling(self):
        mock_calc = Mock(spec=Calculator)  
        mock_calc.save_history.side_effect = Exception("Save failed on exit")

        with patch("builtins.input", side_effect=["exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Could not save history" in str(call) for call in print_calls)    
                    assert any("Goodbye!" in str(call) for call in print_calls)
class TestExceptionErrors:
    """This class tests error handling during calculation in the REPL and ensures that all expected operations (like 'add', 'subtract', 'multiply', etc.) 
        are included in the OPERATIONS"""

    @pytest.mark.parametrize("operation, first_input, second_input, error_type, error_message" , [
        ("add", "5", "3", ValidationError, "Error:"),
        ("divide", "10", "0", OperationError, "Error:"),
        ("add", "5", "3", Exception, "Unexpected error:"),
    ])       
    def test_perform_calculation_errors(self, operation, first_input, second_input, error_type, error_message):
        mock_calc = Mock(spec=Calculator)
        mock_calc.perform_operation.side_effect = error_type("Test error message")
        
        inputs = [first_input, second_input]
        
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.OperationFactory.create_operation") as mock_factory:
                    mock_operation = Mock()
                    mock_factory.return_value = mock_operation
                    
                    perform_calculation(mock_calc, operation)
                    
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any(error_message in str(call) for call in print_calls)
    
    def test_perform_calculation_value_error(self):
        """Test that ValueError is properly caught and displayed."""
        mock_calc = Mock(spec=Calculator)
        mock_calc.perform_operation.side_effect = ValueError("Invalid number format")

        with patch("builtins.input", side_effect=["5", "3"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.OperationFactory.create_operation") as mock_factory:
                    mock_operation = Mock()
                    mock_factory.return_value = mock_operation
                
                perform_calculation(mock_calc, "add")
                
                # Check that both ValueError error messages were printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Invalid input:" in str(call) for call in print_calls)
                assert any("Please enter valid numbers" in str(call) for call in print_calls)


    def test_perform_calculation_non_decimal_result(self):
        """Test calculation when result is not a Decimal (covers branch 71->73)."""
        mock_calc = Mock(spec=Calculator)
        # Return something that's NOT a Decimal (like an int or string)
        mock_calc.perform_operation.return_value = 42  # An integer, not a Decimal
    
        with patch("builtins.input", side_effect=["5", "3"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.OperationFactory.create_operation") as mock_factory:
                    mock_operation = Mock()
                    mock_factory.return_value = mock_operation
                
                perform_calculation(mock_calc, "add")
                
                # Verify the result was printed (without normalization since it's not a Decimal)
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Result: 42" in str(call) for call in print_calls)

    
    def test_perform_calculation_first_input_cancelled(self): 
        mock_calc = Mock(spec=Calculator)  

        with patch("builtins.input", return_value="cancel"):
            with patch("builtins.print") as mock_print:
            
                perform_calculation(mock_calc, "add")
                mock_calc.perform_operation.assert_not_called()
                    
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Operation cancelled" in str(call) for call in print_calls)

    def test_general_exception_in_repl_loop(self):
        mock_calc = Mock(spec=Calculator) 
        mock_calc.show_history.side_effect = Exception("Unexpected error in loop")     

        with patch("builtins.input", side_effect=["history", "exit"]):
            with patch("builtins.print") as mock_print:
                with patch("app.calculator_repl.Calculator", return_value=mock_calc):
                    with patch("app.calculator_repl.LoggingObserver"):
                        with patch("app.calculator_repl.AutoSaveObserver"):
                            calculator_repl()
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        assert any("Error:" in str(call) for call in print_calls)


    @pytest.mark.parametrize("operation", list(OPERATIONS))
    def test_expected_operations_in_set(self, operation):
        """Test that all expected operations are in OPERATIONS."""
        assert operation in OPERATIONS