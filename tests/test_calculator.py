import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

    autosave_observer = AutoSaveObserver(calculator)
    calculator.add_observer(autosave_observer)
    assert autosave_observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

    autosave_observer = AutoSaveObserver(calculator)
    calculator.add_observer(autosave_observer)
    calculator.remove_observer(autosave_observer)
    assert autosave_observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

    # Test show_history
def test_show_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    history = calculator.show_history()
    assert len(history) == 1
    assert "2" in history[0] and "3" in history[0]

def test_show_history_empty(calculator):
    history = calculator.show_history()
    assert history == []

# Test get_history_dataframe
def test_get_history_dataframe(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    df = calculator.get_history_dataframe()
    assert len(df) == 1
    assert df['operation'][0] == 'Addition'

def test_get_history_dataframe_empty(calculator):
    df = calculator.get_history_dataframe()
    assert len(df) == 0

# Test undo/redo edge cases
def test_undo_empty_stack(calculator):
    result = calculator.undo()
    assert result is False

def test_redo_empty_stack(calculator):
    result = calculator.redo()
    assert result is False

def test_multiple_undo_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 5)
    
    # Undo twice
    assert calculator.undo() is True
    assert calculator.undo() is True
    assert len(calculator.history) == 0
    
    # Redo twice
    assert calculator.redo() is True
    assert calculator.redo() is True
    assert len(calculator.history) == 2

# Test different operations
def test_subtraction(calculator):
    operation = OperationFactory.create_operation('subtract')
    calculator.set_operation(operation)
    result = calculator.perform_operation(10, 3)
    assert result == Decimal('7')

def test_multiplication(calculator):
    operation = OperationFactory.create_operation('multiply')
    calculator.set_operation(operation)
    result = calculator.perform_operation(4, 5)
    assert result == Decimal('20')

def test_division(calculator):
    operation = OperationFactory.create_operation('divide')
    calculator.set_operation(operation)
    result = calculator.perform_operation(10, 2)
    assert result == Decimal('5')

def test_division_by_zero(calculator):
    operation = OperationFactory.create_operation('divide')
    calculator.set_operation(operation)
    with pytest.raises(ValidationError):
        calculator.perform_operation(10, 0)

# Test notify_observers
def test_notify_observers(calculator):
    observer = Mock(spec=LoggingObserver)
    calculator.add_observer(observer)
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    
    # Verify observer was notified
    observer.update.assert_called_once()

# Test history size limit
def test_history_max_size(calculator):
    # Set a small max size for testing
    calculator.config.max_history_size = 3
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    # Add more than max
    for i in range(5):
        calculator.perform_operation(i, i)
    
    # Should only keep last 3
    assert len(calculator.history) <= 3

# Test save_history with empty history
@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history_empty(mock_to_csv, calculator):
    calculator.save_history()
    mock_to_csv.assert_called_once()

# Test load_history with non-existent file
@patch('app.calculator.Path.exists', return_value=False)
def test_load_history_no_file(mock_exists, calculator):
    calculator.load_history()
    assert calculator.history == []

# Test load_history with empty CSV
@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_empty_csv(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame()
    calculator.load_history()
    # Should handle empty file gracefully

# Test validation with different invalid inputs
def test_perform_operation_invalid_first_operand(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('abc', 3)

def test_perform_operation_invalid_second_operand(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation(3, 'xyz')

def test_perform_operation_both_invalid(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('abc', 'xyz')

# Test redo stack clears after new operation
def test_redo_stack_clears_on_new_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    
    # Redo stack should have something
    assert len(calculator.redo_stack) > 0
    
    # New operation should clear redo stack
    calculator.perform_operation(5, 5)
    assert len(calculator.redo_stack) == 0