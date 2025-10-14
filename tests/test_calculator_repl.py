########################
# Calculator REPL Tests #
########################

import pytest
from unittest.mock import Mock, patch
from io import StringIO
from decimal import Decimal

from app.calculator_repl import calculator_repl, perform_calculation, get_user_input, OPERATIONS, show_help
from app.calculator import Calculator
from app.exceptions import ValidationError, OperationError