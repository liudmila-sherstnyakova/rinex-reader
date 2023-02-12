import math

from common import normalize_data_string
from navigation.v4.nav_message_type.ION_Klobuchar import IONKlobNavRecord


def test_IONKlobNavRecord_read_lines():
    record = IONKlobNavRecord("SV")
    record.read_epoch_line("    2022 09 29 09 40 27 2.421438694000e-08 2.682209014893e-07-2.026557922363e-06")
    assert record.Alpha0 == 2.421438694000e-08
    assert record.Alpha1 == 2.682209014893e-07
    assert record.Alpha2 == -2.026557922363e-06

    record.read_lines(
        list(map(lambda s: normalize_data_string(s),
                 [
                     "     2.980232238770e-06 1.515520000000e+05-8.028160000000e+05 4.128768000000e+06",
                     "     3.817800000000E+05"
                 ]))
    )
    assert record.message_line.Alpha3 == 2.980232238770e-06
    assert record.message_line.Beta0 == 1.515520000000e+05
    assert record.message_line.Beta1 == -8.028160000000e+05
    assert record.message_line.Beta2 == 4.128768000000e+06

    assert record.message_line.Beta3 == 3.817800000000E+05
    assert math.isnan(record.message_line.region_code)
