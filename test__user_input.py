# test_user_input.py

import itertools
import pytest
from unittest.mock import patch, mock_open
from user_input import get_user_input


def test_valid_input():
    input_values = iter(['0.1', '0.24', '3'])
    with patch('builtins.input', side_effect=input_values):
        result = get_user_input()
    assert result == (0.001, 0.0024, 3)


def test_invalid_input():
    # Use itertools.cycle to create an infinite iterator that repeats the input values
    input_values = itertools.cycle(['invalid', 'invalid', 'invalid'])

    # Patching both 'input' and 'open' functions
    with patch('builtins.input', side_effect=lambda _: next(input_values)), patch('builtins.open', mock_open()):
        # Handling StopIteration explicitly
        with pytest.raises(SystemExit) as sys_exit_exc:
            with pytest.raises(ValueError):
                get_user_input()

    # Check if SystemExit is raised with the expected exit code
    assert sys_exit_exc.type == SystemExit
    assert sys_exit_exc.value.code == 2


def test_script_termination():
    with patch('builtins.input', side_effect=EOFError):
        with pytest.raises(SystemExit) as sys_exit_exc:
            get_user_input()

    # Check if SystemExit is raised with the expected exit code
    assert sys_exit_exc.type == SystemExit
    assert sys_exit_exc.value.code == 1
