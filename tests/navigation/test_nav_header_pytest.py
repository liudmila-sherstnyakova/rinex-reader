from datetime import datetime

from nmbu.rinex.navigation.v3.header import read_navigation_header_v3
from nmbu.rinex.navigation.v4.header import read_navigation_header_v4
from tests import resources_path


def test_read_navigation_header_v3():
    with (resources_path/"header_v3.22p").open() as f:
        first_line = next(f)  # simulate reading first line
        result = read_navigation_header_v3(file=f, version=3.05, file_type='N', gnss='M')
        assert result.version == 3.05
        assert result.file_type == 'N'
        assert result.gnss == 'M'
        assert result.agency == 'Kamilla Brynildsen'
        assert result.created_by == 'TPS2RIN 1.0.28.3459'
        assert result.creation_time == datetime(2022, 10, 6, 13, 44, 21)
        assert len(result.corrections['ION']) == 13
        assert result.corrections['ION']['C8']['X'].alpha0 == 2.4214E-08
        assert result.corrections['ION']['C8']['X'].beta0 == 1.5155E+05
        assert result.corrections['ION']['E']['NO_TIME'].ai0 == -2.0489E-08
        assert result.corrections['ION']['G']['NO_TIME'].alpha0 == 2.0489E-08
        assert len(result.other) == 3


def test_read_navigation_header_v4():
    with (resources_path/"header_v4.22p").open() as f:
        first_line = next(f)  # simulate reading first line
        result = read_navigation_header_v4(file=f, version=4.00, file_type='N', gnss='M')
        assert result.version == 4.00
        assert result.file_type == 'N'
        assert result.gnss == 'M'
        assert result.agency == 'KB'
        assert result.created_by == 'TPS2RIN 1.0.28.3459'
        assert result.creation_time == datetime(2023, 2, 2, 8, 14, 22)
        assert len(result.other) == 2

