from datetime import datetime

import pytest

from nmbu.rinex.navigation.v3.header import read_navigation_header_v3
from nmbu.rinex.navigation.v3.nav_message_type.BDS import BDSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GAL import GALNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GLO import GLONavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GPS import GPSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.IRN import IRNNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.QZS import QZSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.SBAS import SBASNavRecord
from nmbu.rinex.navigation.v3.navigation import __read_epoch_line, read_navigation_blocks_v3
from tests import resources_path

timestamp = datetime(2022, 9, 29, 9, 50, 0).isoformat()


@pytest.mark.parametrize("sv, expected_record_type",
    [
        ('G01', GPSNavRecord),
        ('E01', GALNavRecord),
        ('C01', BDSNavRecord),
        ('J01', QZSNavRecord),
        ('I01', IRNNavRecord),
     ]
)
def test_read_epoch_line(sv, expected_record_type):
    record, valid, size = __read_epoch_line(sv + " 2022 09 29 09 50 00-1.393973361701E-04 3.623767952377E-12 0.000000000000E+00")
    assert isinstance(record, expected_record_type)
    assert record.timestamp == timestamp
    assert record.block_size == expected_record_type.block_size
    assert record.clock_bias == -1.393973361701E-04
    assert record.clock_drift == 3.623767952377E-12
    assert record.clock_drift_rate == 0.000000000000E+00


def test_read_epoch_line__GLO():
    record, valid, size = __read_epoch_line("R01 2022 09 29 09 50 00-1.393973361701E-04 3.623767952377E-12 0.000000000000E+00")
    assert isinstance(record, GLONavRecord)
    assert record.timestamp == timestamp
    assert record.block_size == GLONavRecord.block_size
    assert record.clock_bias == -1.393973361701E-04
    assert record.relative_frequency_bias == 3.623767952377E-12
    assert record.msg_frame_time == 0.000000000000E+00


def test_read_epoch_line__SBAS():
    record, valid, size = __read_epoch_line("S01 2022 09 29 09 50 00-1.393973361701E-04 3.623767952377E-12 0.000000000000E+00")
    assert isinstance(record, SBASNavRecord)
    assert record.timestamp == timestamp
    assert record.block_size == SBASNavRecord.block_size
    assert record.clock_bias == -1.393973361701E-04
    assert record.relative_frequency_bias == 3.623767952377E-12
    assert record.msg_transmission_time == 0.000000000000E+00


def test_read_navigation_blocks_v3__valid():
    with (resources_path/"navigation_v3.22p").open() as f:
        first_line = next(f)  # simulate reading first line
        read_navigation_header_v3(file=f, version=3.05, file_type='N', gnss='M')
        result = read_navigation_blocks_v3(file=f)
        assert result.satellites.keys() == {'C11', 'E05', 'G03', 'R19'}
        assert result.satellites["C11"].keys() == {'2022-09-29T10:00:00'}
        assert result.satellites["E05"].keys() == {'2022-09-29T09:50:00'}
        assert result.satellites["G03"].keys() == {'2022-09-29T12:00:00'}
        assert result.satellites["R19"].keys() == {'2022-09-29T10:45:00'}


def test_read_navigation_blocks_v3__invalid():
    with pytest.raises(ValueError) as e_info:
        with (resources_path/"navigation_v3_invalid.22p").open() as f:
            next(f)  # simulate reading first line
            read_navigation_header_v3(file=f, version=3.05, file_type='N', gnss='M')
            read_navigation_blocks_v3(file=f)
    assert str(e_info.value) == 'Block C112022-09-29T10:00:00 has invalid size.'


