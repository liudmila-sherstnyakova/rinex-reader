import pytest

from nmbu.rinex import reader


# tests for reader.__read_first_line


def test_read_first_line_for_v3_obs_mixed():
    ver, file_type, gnss = reader.\
        __read_first_line("     3.05           OBSERVATION DATA    MIXED               RINEX VERSION / TYPE")
    assert ver == 3.05, 'Incorrect version. Expected 3.05'
    assert file_type == 'O', 'Incorrect file type. Expected O'
    assert gnss == 'M', 'Incorrect version. Expected M'


def test_read_first_line_for_v3_nav_mixed():
    ver, file_type, gnss = reader.\
        __read_first_line("     3.05           NAVIGATION DATA     MIXED               RINEX VERSION / TYPE")
    assert ver == 3.05, 'Incorrect version. Expected 3.05'
    assert file_type == 'N', 'Incorrect file type. Expected N'
    assert gnss == 'M', 'Incorrect version. Expected M'


def test_read_first_line_single_gnss():
    ver, file_type, gnss = reader.\
        __read_first_line("     3.05           NAVIGATION DATA     GPS                 RINEX VERSION / TYPE")
    assert ver == 3.05, 'Incorrect version. Expected 3.05'
    assert file_type == 'N', 'Incorrect file type. Expected N'
    assert gnss == 'G', 'Incorrect version. Expected G'


def test_read_first_line_missing_label():
    with pytest.raises(AssertionError) as e_info:
        reader.__read_first_line("     3.05           NAVIGATION DATA     MIXED               ")
    assert str(e_info.value).startswith("First line is expected to have label")


def test_read_first_line_empty_line():
    with pytest.raises(AssertionError) as e_info:
        reader.__read_first_line("")
    assert str(e_info.value).startswith("First line is expected to have label")


def test_read_first_line_wrong_version():
    with pytest.raises(ValueError) as e_info:
        reader.__read_first_line("     a.05           NAVIGATION DATA     MIXED               RINEX VERSION / TYPE")
    assert str(e_info.value).startswith("Invalid version value in RINEX VERSION / TYPE")


def test_read_first_line_wrong_type():
    with pytest.raises(AssertionError) as e_info:
        reader.__read_first_line("     3.05           METEOROLOGICAL DATA     MIXED           RINEX VERSION / TYPE")
    assert str(e_info.value) == "Unknown file type. Expected 'O' or 'N', but got 'M'"


def test_read_first_line_wrong_gnss():
    with pytest.raises(AssertionError) as e_info:
        reader.__read_first_line("     3.05           NAVIGATION DATA     LNAV                RINEX VERSION / TYPE")
    assert str(e_info.value) == "Unknown GNSS: 'L'"

# tests for reader.read_rinex_file

