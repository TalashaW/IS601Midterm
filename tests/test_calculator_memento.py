########################
# Calculator Memento Tests #
########################

import pytest
import datetime
from decimal import Decimal

from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


@pytest.fixture
def sample_calculation():
    """Fixture providing a sample calculation."""
    return Calculation(
        operation='Addition',
        operand1=Decimal('5'),
        operand2=Decimal('3')
    )


@pytest.fixture
def sample_calculations():
    """Fixture providing multiple sample calculations."""
    return [
        Calculation(operation='Addition', operand1=Decimal('5'), operand2=Decimal('3')),
        Calculation(operation='Subtraction', operand1=Decimal('10'), operand2=Decimal('2')),
        Calculation(operation='Multiplication', operand1=Decimal('4'), operand2=Decimal('2')),
    ]


class TestCalculatorMementoCreation:
    """Tests for CalculatorMemento creation."""
    
    def test_create_empty_memento(self):
        """Test creating a memento with empty history."""
        memento = CalculatorMemento(history=[])
        assert memento.history == []
        assert isinstance(memento.timestamp, datetime.datetime)
    
    def test_create_memento_with_single_calculation(self, sample_calculation):
        """Test creating a memento with one calculation."""
        memento = CalculatorMemento(history=[sample_calculation])
        assert len(memento.history) == 1
        assert memento.history[0] == sample_calculation
    
    def test_create_memento_with_multiple_calculations(self, sample_calculations):
        """Test creating a memento with multiple calculations."""
        memento = CalculatorMemento(history=sample_calculations)
        assert len(memento.history) == 3
        assert memento.history == sample_calculations
    
    def test_timestamp_auto_generated(self):
        """Test that timestamp is automatically generated."""
        before = datetime.datetime.now()
        memento = CalculatorMemento(history=[])
        after = datetime.datetime.now()
        
        assert before <= memento.timestamp <= after
    
    def test_custom_timestamp(self):
        """Test creating memento with custom timestamp."""
        custom_time = datetime.datetime(2024, 1, 1, 12, 0, 0)
        memento = CalculatorMemento(history=[], timestamp=custom_time)
        assert memento.timestamp == custom_time


class TestCalculatorMementoToDictSerialization:
    """Tests for to_dict serialization."""
    
    def test_to_dict_empty_history(self):
        """Test serializing memento with empty history."""
        memento = CalculatorMemento(history=[])
        data = memento.to_dict()
        
        assert 'history' in data
        assert 'timestamp' in data
        assert data['history'] == []
        assert isinstance(data['timestamp'], str)
    
    def test_to_dict_with_calculations(self, sample_calculations):
        """Test serializing memento with calculations."""
        memento = CalculatorMemento(history=sample_calculations)
        data = memento.to_dict()
        
        assert len(data['history']) == 3
        assert all(isinstance(calc, dict) for calc in data['history'])
    
    def test_to_dict_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        custom_time = datetime.datetime(2024, 6, 15, 10, 30, 45)
        memento = CalculatorMemento(history=[], timestamp=custom_time)
        data = memento.to_dict()
        
        assert data['timestamp'] == '2024-06-15T10:30:45'
    
    @pytest.mark.parametrize("num_calculations", [0, 1, 5, 10, 100])
    def test_to_dict_various_history_sizes(self, num_calculations):
        """Test serialization with various history sizes."""
        calculations = [
            Calculation(operation='Addition', operand1=Decimal(i), operand2=Decimal(i))
            for i in range(num_calculations)
        ]
        memento = CalculatorMemento(history=calculations)
        data = memento.to_dict()
        
        assert len(data['history']) == num_calculations


class TestCalculatorMementoFromDictDeserialization:
    """Tests for from_dict deserialization."""
    
    def test_from_dict_empty_history(self):
        """Test deserializing memento with empty history."""
        data = {
            'history': [],
            'timestamp': '2024-01-01T12:00:00'
        }
        memento = CalculatorMemento.from_dict(data)
        
        assert memento.history == []
        assert memento.timestamp == datetime.datetime(2024, 1, 1, 12, 0, 0)
    
    def test_from_dict_with_calculations(self):
        """Test deserializing memento with calculations."""
        data = {
            'history': [
                {
                    'operation': 'Addition',
                    'operand1': '5',
                    'operand2': '3',
                    'result': '8',
                    'timestamp': datetime.datetime.now().isoformat()
                },
                {
                    'operation': 'Subtraction',
                    'operand1': '10',
                    'operand2': '2',
                    'result': '8',
                    'timestamp': datetime.datetime.now().isoformat()
                }
            ],
            'timestamp': '2024-06-15T10:30:45'
        }
        memento = CalculatorMemento.from_dict(data)
        
        assert len(memento.history) == 2
        assert all(isinstance(calc, Calculation) for calc in memento.history)
        assert memento.timestamp == datetime.datetime(2024, 6, 15, 10, 30, 45)
    
    @pytest.mark.parametrize("timestamp_str,expected_datetime", [
        ('2024-01-01T00:00:00', datetime.datetime(2024, 1, 1, 0, 0, 0)),
        ('2024-12-31T23:59:59', datetime.datetime(2024, 12, 31, 23, 59, 59)),
        ('2025-06-15T12:30:45', datetime.datetime(2025, 6, 15, 12, 30, 45)),
    ])
    def test_from_dict_various_timestamps(self, timestamp_str, expected_datetime):
        """Test deserialization with various timestamp formats."""
        data = {
            'history': [],
            'timestamp': timestamp_str
        }
        memento = CalculatorMemento.from_dict(data)
        assert memento.timestamp == expected_datetime


class TestCalculatorMementoRoundTrip:
    """Tests for serialization round-trip (to_dict -> from_dict)."""
    
    def test_roundtrip_empty_history(self):
        """Test round-trip with empty history."""
        original = CalculatorMemento(history=[])
        data = original.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert restored.history == original.history
        assert restored.timestamp == original.timestamp
    
    def test_roundtrip_with_calculations(self, sample_calculations):
        """Test round-trip with calculations."""
        original = CalculatorMemento(history=sample_calculations)
        data = original.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert len(restored.history) == len(original.history)
        for orig_calc, rest_calc in zip(original.history, restored.history):
            assert orig_calc.operand1 == rest_calc.operand1
            assert orig_calc.operand2 == rest_calc.operand2
            assert orig_calc.operation == rest_calc.operation
            assert orig_calc.result == rest_calc.result
    
    @pytest.mark.parametrize("operations", [
        ['Addition'],
        ['Subtraction', 'Multiplication'],
        ['Division', 'Power', 'Root'],
    ])
    def test_roundtrip_various_operations(self, operations):
        """Test round-trip with various operation types."""
        calculations = [
            Calculation(operation=op, operand1=Decimal('10'), operand2=Decimal('2'))
            for op in operations
        ]
        
        original = CalculatorMemento(history=calculations)
        data = original.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert len(restored.history) == len(original.history)
        for i in range(len(operations)):
            assert restored.history[i].operation == original.history[i].operation


class TestCalculatorMementoDataIntegrity:
    """Tests for data integrity and immutability concerns."""
    
    def test_history_independence(self, sample_calculations):
        """Test that memento history is independent of original list."""
        original_list = sample_calculations.copy()
        memento = CalculatorMemento(history=original_list)
        
        # Modify original list
        original_list.append(
            Calculation(operation='Addition', operand1=Decimal('99'), operand2=Decimal('1'))
        )
        
        # Memento should have original length
        assert len(memento.history) == 3
    
    def test_serialized_data_structure(self, sample_calculation):
        """Test that serialized data has correct structure."""
        memento = CalculatorMemento(history=[sample_calculation])
        data = memento.to_dict()
        
        assert isinstance(data, dict)
        assert 'history' in data
        assert 'timestamp' in data
        assert isinstance(data['history'], list)
        assert isinstance(data['timestamp'], str)
    
    def test_calculation_data_preserved(self):
        """Test that calculation data is accurately preserved."""
        calc = Calculation(
            operation='Multiplication',
            operand1=Decimal('123.456'),
            operand2=Decimal('789.012')
        )
        
        memento = CalculatorMemento(history=[calc])
        data = memento.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        restored_calc = restored.history[0]
        assert restored_calc.operand1 == calc.operand1
        assert restored_calc.operand2 == calc.operand2
        assert restored_calc.operation == calc.operation
        assert restored_calc.result == calc.result


class TestCalculatorMementoEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_large_history(self):
        """Test memento with large history."""
        large_history = [
            Calculation(operation='Addition', operand1=Decimal(i), operand2=Decimal(i))
            for i in range(1000)
        ]
        
        memento = CalculatorMemento(history=large_history)
        data = memento.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert len(restored.history) == 1000
    
    def test_decimal_precision_preserved(self):
        """Test that decimal precision is preserved through serial"""