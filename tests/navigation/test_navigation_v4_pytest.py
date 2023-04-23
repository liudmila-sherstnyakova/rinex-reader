from datetime import datetime

import pytest

from nmbu.rinex.navigation.v4.header import read_navigation_header_v4
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV1 import BDSCNAV1Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV2 import BDSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV3 import BDSCNAV3Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_D1_D2 import BDSD1D2Record
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV import GPSCNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV2 import GPSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.GPS_LNAV import GPSLNAVRecord
from nmbu.rinex.navigation.v4.navigation import read_navigation_blocks_v4, __read_start_line
from tests import resources_path

timestamp = datetime(2022, 9, 29, 9, 50, 0).isoformat()


@pytest.mark.parametrize("sv, navtype, expected_record_type",
    [
        ('G01','LNAV', GPSLNAVRecord),
        ('G02','CNAV', GPSCNAVRecord),
        ('G03','CNV2', GPSCNAV2Record),
        ('C01','CNV1', BDSCNAV1Record),
        ('C03','CNV2', BDSCNAV2Record),
        ('C03','CNV3', BDSCNAV3Record),
        ('C04','D1', BDSD1D2Record),
        ('C05','D2', BDSD1D2Record),
     ]
)
def test_read_epoch_line(sv, navtype, expected_record_type):
    record, valid, size = __read_start_line("> EPH {sv:s} {navtype:s}".format(sv=sv, navtype=navtype))
    assert isinstance(record, expected_record_type)
    assert record.block_size == expected_record_type.block_size

    record.read_epoch_line(sv + " 2022 09 29 09 50 00 2.758218906820e-04-6.366462912410e-12 0.000000000000e+00")
    assert record.timestamp == timestamp
    assert record.clock_bias == 2.758218906820e-04
    assert record.clock_drift == -6.366462912410e-12
    assert record.clock_drift_rate == 0.000000000000E+00


def test_read_navigation_blocks_v4__valid():
    with (resources_path/"navigation_v4.22p").open() as f:
        first_line = next(f)  # simulate reading first line
        read_navigation_header_v4(file=f, version=4.00, file_type='N', gnss='M')
        result = read_navigation_blocks_v4(file=f)
        assert result.satellites.keys() == {'G01', 'C05', 'E09'}
        assert result.satellites["G01"].keys() == {'2022-09-29T09:59:44'}
        assert result.satellites["C05"].keys() == {'2022-09-29T09:00:00'}
        assert result.satellites["E09"].keys() == {'2022-09-29T09:20:00'}
        assert result.satellites["E09"]['2022-09-29T09:20:00'].TGD == result.satellites["E09"]['2022-09-29T09:20:00'].BGD_E5b_E1

        assert result.corrections.keys() == {'STO', 'ION', 'EOP'}
        assert result.corrections['STO'].keys() == {'G'}
        assert result.corrections['STO']["G"].keys() == {'2022-09-24T19:50:24'}
        assert result.corrections['ION'].keys() == {'C06','C05'}
        assert result.corrections['ION']["C06"].keys() == {'2022-09-29T09:40:42'}
        assert result.corrections['EOP'].keys() == {'J01'}
        assert result.corrections['EOP']['J01'].keys() == {'2022-09-29T09:40:42'}


def test_read_navigation_blocks_v4__invalid():
    with pytest.raises(ValueError) as e_info:
        with (resources_path/"navigation_v4_invalid.22p").open() as f:
            next(f)  # simulate reading first line
            read_navigation_header_v4(file=f, version=3.05, file_type='N', gnss='M')
            read_navigation_blocks_v4(file=f)
    assert str(e_info.value).__contains__("Navigation file seems to be invalid. Stopped reading at line")


