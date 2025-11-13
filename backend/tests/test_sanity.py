"""
Sanity test to verify backend test infrastructure.
"""
import pytest


def test_python_version():
    """Verify Python version is 3.11+"""
    import sys
    assert sys.version_info >= (3, 11), "Python 3.11+ required"


def test_imports():
    """Verify all core dependencies can be imported"""
    import fastapi
    import playwright
    import openpyxl
    import pydantic
    
    assert fastapi is not None
    assert playwright is not None
    assert openpyxl is not None
    assert pydantic is not None


def test_sample():
    """Sample test to ensure pytest works"""
    assert 1 + 1 == 2
