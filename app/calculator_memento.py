########################
# Calculator Memento    #
########################

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List

from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """
    Memento for storing calculator history snapshots.
    
    This class implements the Memento design pattern to store a snapshot of the
    calculator state for undo/redo functionality.
    
    Example:
        >>> calc = Calculator()
        >>> calc.perform_operation(5, 3)  # History: [5+3=8]
        >>> calc.undo()  # History: []
        >>> calc.redo()  # History: [5+3=8]
    """
    
    history: List[Calculation] 
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)  
    """History captures a snapshot of the calculations at the moment of creation.
        Timestamp automatically records the default state at creation.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memento to dictionary.

        This method serializes the memento's state into a dictionary format,
        making it easy to store or transmit as JSON or CSV.

        Returns:
            Dict[str, Any]: A dictionary containing the serialized state of the memento.
        """
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':
        """
        Create memento from dictionary.

        This class method deserializes a dictionary to rebuilds an
        instance that restores the calculator's history and timestamp.

        Args:
            data (Dict[str, Any]): Dictionary containing serialized memento data.

        Returns:
            CalculatorMemento: A new instance of CalculatorMemento with restored state.
        """
        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )
