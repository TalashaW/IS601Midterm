########################
# Calculator REPL Tests #
########################

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.calculator_repl import show_help,  get_user_input, perform_calculation, calculator_repl, OPERATIONS
from app.exceptions import ValidationError, OperationError


class TestShowHelp:
    """Test show_help function."""
    def test_show_help_displays_commands(self):
        """Test that show_help prints available commands."""
        with patch('builtins.print') as mock_print:
            show_help()
            assert mock_print.called
            # The verifies that the help commands were printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Available commands:" in str(call) for call in calls)

class TestUserInput:
    """Test get_user_input function."""
    @pytest.mark.parametrize("5", "5 ")
    def test_get_user_input(user_input):
        """Test that the function can handle input with or without spaces """
        with patch('builtins.input', return_value=user_input):
            with patch('builtins.print'):
                result = get_user_input("Enter: ")
                assert result is user_input
    
    @pytest.mark.parametrize("user_input", ["cancel", "CANCEL"])
    def test_get_user_input_cancel(user_input):
        """Test that typing 'cancel' (case-insensitive) returns None."""
        with patch('builtins.input', return_value=user_input):
            with patch('builtins.print'):
                result = get_user_input("Enter: ")
                assert result is None
    
class TestPerformCalculation:
    """Test perform_calculation function."""


    def test_perform_calculation_success(self):
        """Test successful calculation execution."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('8')
        
        with patch('builtins.input', side_effect=["5", "3"]):
            with patch('builtins.print') as mock_print:
                perform_calculation(mock_calc, "add")
                
        mock_calc.set_operation.assert_called_once()
        mock_calc.perform_operation.assert_called_once_with("5", "3")
    
    def test_perform_calculation_cancel_first_input(self):
        """Test cancelling at first number input."""
        mock_calc = Mock()
        
        with patch('builtins.input', return_value="cancel"):
            with patch('builtins.print'):
                perform_calculation(mock_calc, "add")
        
        mock_calc.perform_operation.assert_not_called()
    
    def test_perform_calculation_cancel_second_input(self):
        """Test cancelling at second number input."""
        mock_calc = Mock()
        
        with patch('builtins.input', side_effect=["5", "cancel"]):
            with patch('builtins.print'):
                perform_calculation(mock_calc, "add")
        
        mock_calc.perform_operation.assert_not_called()
    
    def test_perform_calculation_validation_error(self):
        """Test handling of ValidationError."""
        mock_calc = Mock()
        mock_calc.perform_operation.side_effect = ValidationError("Invalid number")
        
        with patch('builtins.input', side_effect=["5", "abc"]):
            with patch('builtins.print') as mock_print:
                perform_calculation(mock_calc, "add")
                
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error:" in str(call) for call in calls)
    
    def test_perform_calculation_operation_error(self):
        """Test handling of OperationError."""
        mock_calc = Mock()
        mock_calc.perform_operation.side_effect = OperationError("Division by zero")
        
        with patch('builtins.input', side_effect=["10", "0"]):
            with patch('builtins.print') as mock_print:
                perform_calculation(mock_calc, "divide")
                
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error:" in str(call) for call in calls)
    
    def test_perform_calculation_decimal_normalization(self):
        """Test that Decimal results are normalized."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('8.00')
        
        with patch('builtins.input', side_effect=["5", "3"]):
            with patch('builtins.print') as mock_print:
                perform_calculation(mock_calc, "add")
                
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Result:" in str(call) for call in calls)

class TestCalculatorREPL:
    """Integration tests for calculator_repl function."""
    
    def test_repl_exit_command(self):
        """Test that 'exit' command exits gracefully."""
        with patch('builtins.input', return_value="exit"):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    calculator_repl()
                    MockCalc.return_value.save_history.assert_called()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Goodbye!" in str(call) for call in calls)
    
    def test_repl_exit_save_error(self):
        """Test handling of save error on exit."""
        with patch('builtins.input', return_value="exit"):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.save_history.side_effect = Exception("Save failed")
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Warning: Could not save history" in str(call) for call in calls)
      
    def test_repl_empty_command(self):
        """Test empty command is skipped."""
        with patch('builtins.input', side_effect=["", "exit"]):
            with patch('builtins.print'):
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
    
    def test_repl_history_empty(self):
        """Test 'history' command with no calculations."""
        with patch('builtins.input', side_effect=["history", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.show_history.return_value = []
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("No calculations in history" in str(call) for call in calls)
    
    def test_repl_history_with_entries(self):
        """Test 'history' command displays calculations."""
        with patch('builtins.input', side_effect=["history", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.show_history.return_value = [
                        "Addition(2, 3) = 5",
                        "Subtraction(10, 4) = 6"
                    ]
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Calculation History:" in str(call) for call in calls)
    
    def test_repl_clear_command(self):
        """Test 'clear' command clears history."""
        with patch('builtins.input', side_effect=["clear", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    calculator_repl()
                    MockCalc.return_value.clear_history.assert_called_once()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("History cleared" in str(call) for call in calls)
    
    def test_repl_undo_success(self):
        """Test 'undo' command when operation can be undone."""
        with patch('builtins.input', side_effect=["undo", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.undo.return_value = True
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Operation undone" in str(call) for call in calls)
    
    def test_repl_undo_nothing_to_undo(self):
        """Test 'undo' command when nothing to undo."""
        with patch('builtins.input', side_effect=["undo", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.undo.return_value = False
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Nothing to undo" in str(call) for call in calls)
    
    def test_repl_redo_success(self):
        """Test 'redo' command when operation can be redone."""
        with patch('builtins.input', side_effect=["redo", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.redo.return_value = True
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Operation redone" in str(call) for call in calls)
    
    def test_repl_redo_nothing_to_redo(self):
        """Test 'redo' command when nothing to redo."""
        with patch('builtins.input', side_effect=["redo", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.redo.return_value = False
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Nothing to redo" in str(call) for call in calls)
    
    def test_repl_save_success(self):
        """Test 'save' command successfully saves."""
        with patch('builtins.input', side_effect=["save", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("History saved successfully" in str(call) for call in calls)
    
    def test_repl_save_error(self):
        """Test 'save' command with error."""
        with patch('builtins.input', side_effect=["save", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.save_history.side_effect = [
                        Exception("Save failed"), None
                    ]
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error saving history" in str(call) for call in calls)
    
    def test_repl_load_success(self):
        """Test 'load' command successfully loads."""
        with patch('builtins.input', side_effect=["load", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("History loaded successfully" in str(call) for call in calls)
    
    """def test_repl_load_error(self):
        Test 'load' command with error.
        with patch('builtins.input', side_effect=["load", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.load_history.side_effect = [
                        None, Exception("Load failed")
                    ]
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error loading history" in str(call) for call in calls) """
    
    @pytest.mark.parametrize("operation", list(OPERATIONS))
    def test_repl_all_operations(self, operation):
        """Test all arithmetic operations work."""
        with patch('builtins.input', side_effect=[operation, "6", "2", "exit"]):
            with patch('builtins.print'):
                with patch('app.calculator_repl.Calculator') as MockCalc:
                    MockCalc.return_value.perform_operation.return_value = Decimal('3')
                    calculator_repl()
                    MockCalc.return_value.set_operation.assert_called_once()
    
    def test_repl_unknown_command(self):
        """Test unknown command displays error."""
        with patch('builtins.input', side_effect=["unknown", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Unknown command" in str(call) and "unknown" in str(call) 
                   for call in calls)
    
    def test_repl_keyboard_interrupt(self):
        """Test KeyboardInterrupt is handled gracefully."""
        with patch('builtins.input', side_effect=[KeyboardInterrupt(), "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Operation cancelled" in str(call) for call in calls)
    
    def test_repl_eof_error(self):
        """Test EOFError exits gracefully."""
        with patch('builtins.input', side_effect=EOFError()):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Input terminated" in str(call) for call in calls)
    
    def test_repl_general_exception_in_loop(self):
        """Test general exception in main loop."""
        with patch('builtins.input', side_effect=["add", "exit"]):
            with patch('builtins.print') as mock_print:
                with patch('app.calculator_repl.Calculator'):
                    with patch('app.calculator_repl.perform_calculation', 
                              side_effect=Exception("Test error")):
                        calculator_repl()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error:" in str(call) for call in calls)
    
    def test_repl_initialization_error(self):
        """Test fatal error during initialization."""
        with patch('app.calculator_repl.Calculator', side_effect=Exception("Init failed")):
            with patch('builtins.print') as mock_print:
                with patch('logging.error') as mock_log:
                    with pytest.raises(Exception, match="Init failed"):
                        calculator_repl()
                    mock_log.assert_called()
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Fatal error:" in str(call) for call in calls)