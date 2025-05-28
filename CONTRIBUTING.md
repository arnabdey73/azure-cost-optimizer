# Contributing to Azure Cost Optimizer

Thank you for your interest in contributing to the Azure Cost Optimizer project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list to avoid duplicates. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and the behavior you expected**
- **Include screenshots and animated GIFs if possible**
- **Include details about your environment**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **Specify which version of the project you're using**
- **Specify the name and version of the OS you're using**

### Pull Requests

- Fill in the required template
- Follow the coding standards
- Include appropriate test cases
- Update documentation as needed
- End all files with a newline
- Place requires in the following order:
  - Built-in packages
  - Related third-party packages
  - Local application/library specific imports
- Update the README.md with details of changes to the interface

## Development Environment Setup

1. **Fork the Repository**
   - Fork the repository on GitHub
   - Clone your fork locally

2. **Set Up Development Environment**
   ```bash
   # Clone your fork
   git clone https://github.com/YOUR-USERNAME/azure-cost-optimizer.git
   cd azure-cost-optimizer
   
   # Add the original repository as a remote
   git remote add upstream https://github.com/arnabdey73/azure-cost-optimizer.git
   
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Configure Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Create a Branch for Your Feature**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding standards. We use the following tools to enforce coding standards:

- **Black** for code formatting
- **Flake8** for style guide enforcement
- **isort** for import sorting
- **mypy** for static type checking

Run the linting tools before submitting a pull request:

```bash
# Format with Black
black src tests

# Check with Flake8
flake8 src tests

# Sort imports
isort src tests

# Type checking
mypy src
```

### Python Version Compatibility

Code must be compatible with Python 3.8 and above.

### Type Hinting

Use type hints for all function parameters and return values:

```python
def get_cost_by_resource(self, start_date: str, end_date: str, granularity: str = "Daily") -> dict:
    """
    Query cost data by resource between start_date and end_date.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Data granularity (Daily, Monthly, etc.)
        
    Returns:
        Cost management query response
    """
```

## Pull Request Process

1. **Update your fork** with the latest from upstream:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation

4. **Ensure all tests pass**:
   ```bash
   pytest
   ```

5. **Run linting tools**:
   ```bash
   black src tests
   flake8 src tests
   isort src tests
   ```

6. **Commit your changes** following conventional commits:
   ```bash
   git commit -m "feat: add new cost anomaly detection algorithm"
   ```
   
   Commit message types:
   - **feat**: A new feature
   - **fix**: A bug fix
   - **docs**: Documentation only changes
   - **style**: Changes that do not affect the meaning of the code
   - **refactor**: A code change that neither fixes a bug nor adds a feature
   - **perf**: A code change that improves performance
   - **test**: Adding missing tests or correcting existing tests
   - **chore**: Changes to the build process or auxiliary tools

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a pull request** to the main repository.
   - Fill in the provided template
   - Reference any related issues
   - Request review from project maintainers

## Testing Guidelines

### Test Framework

We use pytest for testing. All tests should be placed in the `tests` directory following the same structure as the source code.

### Test Coverage

Aim for at least 80% test coverage for new code. Run test coverage report:

```bash
pytest --cov=src tests/
```

### Testing Best Practices

- **Write unit tests** for individual functions and classes
- **Use mocks** for external dependencies
- **Test error cases** as well as success cases
- **Test edge cases** and boundary conditions
- **Keep tests isolated** from each other

### Example Test

```python
def test_detect_idle_vms():
    # Mock the AzureCostClient
    class MockClient:
        def query_log_analytics(self, query):
            # Return mock data
            return [
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm1", "avgCpu": 2.5},
                {"ResourceId": "/subscriptions/123/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm2", "avgCpu": 10.5}
            ]
    
    # Test function
    results = detect_idle_vms(MockClient(), "2023-01-01", "2023-01-07", cpu_threshold=5)
    
    # Should only return the VM with CPU < threshold (5)
    assert len(results) == 1
    assert results[0]["resourceId"].endswith("vm1")
    assert results[0]["averageCpu"] == 2.5
```

## Documentation Guidelines

### Code Documentation

- Use docstrings for all public classes and methods
- Follow the Google style for docstrings
- Include type information in docstrings

```python
def query_log_analytics(self, query: str, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Execute a query against Log Analytics workspace
    
    Args:
        query: The KQL query string
        workspace_id: Optional workspace ID (defaults to config)
            
    Returns:
        List of result rows
        
    Raises:
        ValueError: If Log Analytics workspace ID is not provided
    """
```

### Project Documentation

- Keep README.md up to date with new features
- Update architecture documentation for design changes
- Add examples for new functionality
- Ensure API reference is current

Thank you for contributing to the Azure Cost Optimizer project!
