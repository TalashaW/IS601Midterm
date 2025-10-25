# Calculator Application

A robust, feature-rich command-line calculator application built with Python, implementing multiple design patterns and best practices for software development.

---

## Project Overview

This advanced calculator application focuses on building an advanced calculator application with various arithmetic operations, a command-line interface (REPL), and robust error handling. You'll use several design patterns (Factory, Memento, Observer) and implement features like undo/redo, logging, history management, and CI/CD pipelines.

### Key Features

- Multiple arithmetic operations: Addition, subtraction, multiplication, division, power, root, modulus, integer division, percentage, and absolute difference
- Interactive REPL interface: Command-line interface with colorful output using Colorama
- History management: Track, save, load, and clear calculation history
- Undo/Redo functionality: Revert or reapply operations using the Memento pattern
- Observer pattern: Real-time logging and auto-save capabilities
- Configuration management: Flexible settings via environment variables
- Comprehensive testing: Unit tests with high code coverage
- CI/CD pipeline: Automated testing with GitHub Actions

---

## Installation Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create Virtual Environment

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages include:**

- `pandas` - Data manipulation and CSV handling
- `python-dotenv` - Environment variable management
- `colorama` - Colored terminal output
- `pytest` - Testing framework
- `pytest-cov` - Test coverage reporting

---

## Configuration Setup

### Creating the .env File

Create a `.env` file in the project root directory with the following environment variables:

```bash
# .env
CALCULATOR_LOG_DIR=./logs
CALCULATOR_HISTORY_DIR=./history
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8
```

### Configuration Options

| Variable                      | Description                      | Default     |
| ----------------------------- | -------------------------------- | ----------- |
| `CALCULATOR_LOG_DIR`          | Directory for log files          | `./logs`    |
| `CALCULATOR_HISTORY_DIR`      | Directory for history files      | `./history` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Maximum history entries          | `1000`      |
| `CALCULATOR_AUTO_SAVE`        | Auto-save history on calculation | `true`      |
| `CALCULATOR_PRECISION`        | Decimal precision                | `10`        |
| `CALCULATOR_MAX_INPUT_VALUE`  | Maximum allowed input            | `1e999`     |
| `CALCULATOR_DEFAULT_ENCODING` | File encoding                    | `utf-8`     |

**Note:** The application will create the `logs` and `history` directories automatically if they don't exist.

### Configuring Logging

The logging system is configured automatically based on your `.env` settings:

- **Log Location**: Defined by `CALCULATOR_LOG_DIR`
- **Log File**: `calculator.log` in the log directory
- **Log Format**: `%(asctime)s - %(levelname)s - %(message)s`
- **Log Level**: INFO

All operations, errors, and system events are logged to the configured log file for debugging and auditing purposes.

---

## Usage Guide

### Starting the Calculator

```bash
python main.py
```

or

```bash
python -m app.main
```

### Available Commands

#### Arithmetic Operations

```
add         - Addition (a + b)
subtract    - Subtraction (a - b)
multiply    - Multiplication (a × b)
divide      - Division (a ÷ b)
power       - Exponentiation (a ^ b)
root        - Root calculation (root b of a)
modulus     - Modulo operation (a % b)
intdiv      - Integer division (a // b)
percentage  - Percentage ((a/b) × 100)
absdiff     - Absolute difference (|a - b|)
```

#### Session Management

```
history     - Display calculation history
clear       - Clear calculation history
undo        - Undo the last operation
redo        - Redo the last undone operation
save        - Save history to CSV file
load        - Load history from CSV file
help        - Show all available commands
exit        - Exit the calculator
```

### Example Usage Session

```
Calculator started. Type 'help' for commands.

Enter command: add
Enter numbers (or 'cancel' to abort):
First number: 2
Second number: 3
Result: 5

Enter command: divide
Enter numbers (or 'cancel' to abort):
First number: 10
Second number: 2
Result: 5

Enter command: history
Calculation History:
  1. Addition(2, 3) = 5
  2. Division(10, 2) = 5

Enter command: power
Enter numbers (or 'cancel' to abort):
First number: 2
Second number: 8
Result: 256

Enter command: undo
Operation undone

Enter command: history
Calculation History:
  1. Addition(2, 3) = 5
  2. Division(10, 2) = 5

Enter command: redo
Operation redone

Enter command: save
History saved successfully

Enter command: exit
History saved successfully.
Goodbye!
```

### Canceling Operations

Type `cancel` at any input prompt to abort the current operation:

```
Enter command: multiply
Enter numbers (or 'cancel' to abort):
First number: cancel
Operation cancelled
```

---

## Testing Instructions

### Running All Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

### Running Specific Test Files

```bash
# Test calculator functionality
pytest tests/test_calculator.py

# Test REPL interface
pytest tests/test_calculator_repl.py

# Test operations
pytest tests/test_operations.py

# Test configuration
pytest tests/test_calculator_config.py
```

### Running Tests with Verbose Output

```bash
pytest -v
```

### Checking Test Coverage

Generate an HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Expected Coverage

The project aims for 100% test coverage across all modules:

- `calculation.py` - 100%
- `calculator.py` - 88%+
- `calculator_repl.py` - 100%
- `calculator_config.py` - 88%+
- `operations.py` - 79%+

---

## CI/CD Information

### GitHub Actions Workflow

The project uses GitHub Actions for continuous integration and deployment.

**Workflow File:** `.github/workflows/python-app.yml`

**Automated Steps:**

1. Code Checkout - Fetches the latest code
2. Python Setup - Configures Python 3.10 environment
3. Dependency Installation - Installs all required packages
4. Testing - Executes all unit tests
5. Coverage Report - Generates test coverage statistics

**Trigger Events:**

- Push to `main` branch
- Pull requests to `main` branch
- Manual workflow dispatch

**Status Badge:**

```markdown
![Tests](https://github.com/<username>/<repo>/workflows/Python%20application/badge.svg)
```

### Running CI/CD Locally

Simulate the CI/CD pipeline on your local machine:

```bash
# Install dependencies
pip install -r requirements.txt

# Run linting
pylint app/

# Run tests with coverage
pytest --cov=app --cov-report=term-missing
```

---

## Project Structure

```
calculator-project/
├── app/
│   ├── __init__.py
│   ├── calculation.py          # Calculation model
│   ├── calculator.py            # Main calculator class
│   ├── calculator_config.py    # Configuration management
│   ├── calculator_memento.py   # Memento pattern for undo/redo
│   ├── calculator_repl.py      # Command-line interface
│   ├── exceptions.py            # Custom exceptions
│   ├── history.py               # Observer pattern implementation
│   ├── input_validators.py     # Input validation
│   ├── operations.py            # Operation classes (Factory pattern)
│   └── main.py                  # Application entry point
├── tests/
│   ├── __init__.py
│   ├── test_calculation.py
│   ├── test_calculator.py
│   ├── test_calculator_config.py
│   ├── test_calculator_repl.py
│   └── test_operations.py
├── .env                         # Environment variables (create this)
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

---

## Design Patterns Used

### Factory Pattern (operations.py)

Creates operation objects dynamically based on user input. Simplifies adding new operations.

### Strategy Pattern (operations.py)

Allows switching between different calculation strategies. Each operation is a separate strategy.

### Observer Pattern (history.py)

Implements logging and auto-save functionality. Observers are notified when calculations occur.

### Memento Pattern (calculator_memento.py)

Implements undo/redo functionality. Stores and restores calculator state.

---

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError: No module named 'colorama'**

```bash
pip install colorama
```

**Issue: Tests failing due to file paths**

```bash
# Run tests from the project root directory
cd /path/to/project
pytest
```

**Issue: Colorama colors not showing on Windows**

```bash
# Run in Windows Terminal or update Command Prompt
# Or disable colors in the code temporarily
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

---

## Acknowledgments

- Design patterns inspired by Gang of Four
- Testing framework: pytest
- CI/CD: GitHub Actions
- Color output: Colorama library
