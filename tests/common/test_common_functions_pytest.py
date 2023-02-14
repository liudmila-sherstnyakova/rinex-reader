import pytest

from nmbu.rinex.common import normalize_data_string, str2float


def test_normalize_data_string():
    assert len(normalize_data_string("a")) == 80
    assert normalize_data_string('a') == 'a' + ' ' * 79
    assert normalize_data_string("    a").startswith('a')


def test_str2float():
    assert str2float('2.0', 'exception') == 2.0
    with pytest.raises(ValueError) as e_info:
        str2float('1ab', 'exception message')
    assert str(e_info.value) == 'exception message'
