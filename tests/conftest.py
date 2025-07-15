import pytest

def pytest_addoption(parser):
    parser.addoption("--benchmark", action="store_true", help="run benchmark tests")
