########################
# History Management    #
########################

from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    This class defines the interface for observers that monitor and react to
    new calculation events. Implementing classes must provide an update method
    to handle the received Calculation instance.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle new calculation event.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to a file.
    
    Implements the Observer pattern by listening for new calculations and logging
    their details to a log file using Python's logging module.
    
    Logged Information:
        - Operation name (e.g., "Addition", "Modulus")
        - Operand values
        - Result value
    
    Example Log Entry:
        2025-01-15 10:30:45 - INFO - Calculation performed: Addition (5, 3) = 8
    """

    def update(self, calculation: Calculation) -> None:
        """
        Log calculation details.

        This method is called whenever a new calculation is performed. It records
        the operation, operands, and result in the log file.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = "
            f"{calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations.
    
    Implements the Observer pattern by listening for new calculations and
    triggering an automatic save of the calculation history if the auto-save
    feature is enabled in the configuration.
    
    Behavior:
        - Checks config.auto_save flag before saving
        - Uses pandas to save history to CSV
        - Logs auto-save events
    
    Args:
        calculator: Calculator instance with 'config' and 'save_history' attributes
    
    Raises:
        TypeError: If calculator lacks required attributes
    """

    def __init__(self, calculator: Any):
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Any): The calculator instance to interact with.
                Must have 'config' and 'save_history' attributes.

        Raises:
            TypeError: If the calculator does not have the required attributes.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        """
        Trigger auto-save.

        This method is called whenever a new calculation is performed. If the
        auto-save feature is enabled, it saves the current calculation history.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")
