import pytest
import datetime
from decimal import Decimal
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


def test_memento_initialization():
    """This function tests that the CclculatorMemento 
    initialized correctly when given a non empty history."""
    calc = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    memento = CalculatorMemento(history=[calc])
    
    """The number of calculation objects in the memento history and validates a timestamp is
        created upon initialization"""
    
    assert len(memento.history) == 1
    assert isinstance(memento.timestamp, datetime.datetime)

def test_memento_empty_history():
    "This tests that the CalculatorMemento initializes correctly with an empty history list"

    """A new instance of the CalculatorMemento class is created and passed
        through an empty list and is verified as an empty list through an assertion"""
    memento = CalculatorMemento(history=[])
    assert memento.history == []

# Test to_dict serialization
def test_memento_to_dict():
    """tests that the to_dict method correctly serializes it's attributes.
    It verifies that both history and timestamp keys are availablein the dictionary,
    that history contains only one serialized calculation, and timestamp is serialzied as a string
    """

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
    """
    Test that the `from_dict` class method correctly reconstructs a CalculatorMemento object
    from a dictionary produced by `to_dict`."""

    calc = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    original = CalculatorMemento(history=[calc])
    
    # Serialize and deserialize
    data = original.to_dict()
    restored = CalculatorMemento.from_dict(data)
    
    assert len(restored.history) == 1
    assert restored.history[0].operation == "Addition"
    assert restored.history[0].operand1 == Decimal('2')
    assert restored.history[0].operand2 == Decimal('3')

    """
    Test that `from_dict` correctly handles an empty history list.
    """
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
    """
    Test full round-trip of serializing a CalculatorMemento to a dictionary
    and deserializing it back using from_dict.
    """
    calc1 = Calculation(operation="Addition", operand1=Decimal('2'), operand2=Decimal('3'))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal('4'), operand2=Decimal('5'))
    
    original = CalculatorMemento(history=[calc1, calc2])
    data = original.to_dict()
    restored = CalculatorMemento.from_dict(data)
    
    assert len(restored.history) == 2
    assert restored.history[0].operation == "Addition"
    assert restored.history[1].operation == "Multiplication"
    assert restored.timestamp == original.timestamp