import pytest
import datetime
from decimal import Decimal
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation

# Test CalculatorMemento initialization
def test_memento_initialization():
    calc = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    memento = CalculatorMemento(history=[calc])
    
    assert len(memento.history) == 1
    assert isinstance(memento.timestamp, datetime.datetime)

def test_memento_empty_history():
    memento = CalculatorMemento(history=[])
    assert memento.history == []

# Test to_dict serialization
def test_memento_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    memento = CalculatorMemento(history=[calc])
    
    data = memento.to_dict()
    
    assert 'history' in data
    assert 'timestamp' in data
    assert len(data['history']) == 1
    assert isinstance(data['timestamp'], str)

def test_memento_to_dict_empty():
    memento = CalculatorMemento(history=[])
    data = memento.to_dict()
    
    assert data['history'] == []
    assert 'timestamp' in data

# Test from_dict deserialization
def test_memento_from_dict():
    calc = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    original = CalculatorMemento(history=[calc])
    
    # Serialize and deserialize
    data = original.to_dict()
    restored = CalculatorMemento.from_dict(data)
    
    assert len(restored.history) == 1
    assert restored.history[0].operation == "Addition"
    assert restored.history[0].operand1 == Decimal('2')
    assert restored.history[0].operand2 == Decimal('3')

def test_memento_from_dict_empty():
    data = {
        'history': [],
        'timestamp': datetime.datetime.now().isoformat()
    }
    memento = CalculatorMemento.from_dict(data)
    
    assert memento.history == []
    assert isinstance(memento.timestamp, datetime.datetime)

# Test round-trip (serialize then deserialize)
def test_memento_round_trip():
    calc1 = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal('4'), operand2=Decimal('5'))
    
    original = CalculatorMemento(history=[calc1, calc2])
    data = original.to_dict()
    restored = CalculatorMemento.from_dict(data)
    
    assert len(restored.history) == 2
    assert restored.history[0].operation == "Addition"
    assert restored.history[1].operation == "Multiplication"
    assert restored.timestamp == original.timestamp