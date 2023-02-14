from nmbu.rinex.common import normalize_data_string
from nmbu.rinex.navigation.v3.nav_message_type.GPS import GPSNavRecord
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV import GPSCNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV2 import GPSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.GPS_LNAV import GPSLNAVRecord

### V3 ###

def test_GPSNavRecord_read_lines():
    record = GPSNavRecord("SV", "2022-09-29T10:00:00")
    record.read_lines(
        list(map(lambda s: normalize_data_string(s),
                 [
                     "     5.500000000000E+01 1.612500000000E+01 4.391254341941E-09 1.650293527635E+00",
                     "     7.506459951401E-07 4.497775575146E-03 8.512288331985E-06 5.153542041779E+03",
                     "     3.888000000000E+05-1.247972249985E-07 1.397849200567E+00-1.862645149231E-09",
                     "     9.751815851645E-01 2.221875000000E+02 1.064872642026E+00-7.908186550570E-09",
                     "     5.371652322309E-10 1.000000000000E+00 2.229000000000E+03 0.000000000000E+00",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     3.817800000000E+05 4.000000000000E+00"
                 ]))
    )
    assert record.orbit_data.IODE == 5.500000000000E+01
    assert record.orbit_data.Crs == 1.612500000000E+01
    assert record.orbit_data.Delta_n == 4.391254341941E-09
    assert record.orbit_data.M0 == 1.650293527635E+00

    assert record.orbit_data.Cuc == 7.506459951401E-07
    assert record.orbit_data.e == 4.497775575146E-03
    assert record.orbit_data.Cus == 8.512288331985E-06
    assert record.orbit_data.sqrt_A == 5.153542041779E+03

    assert record.orbit_data.Toe == 3.888000000000E+05
    assert record.orbit_data.Cic == -1.247972249985E-07
    assert record.orbit_data.OMEGA0 == 1.397849200567E+00
    assert record.orbit_data.Cis == -1.862645149231E-09

    assert record.orbit_data.i0 == 9.751815851645E-01
    assert record.orbit_data.Crc == 2.221875000000E+02
    assert record.orbit_data.omega == 1.064872642026E+00
    assert record.orbit_data.OMEGA_DOT == -7.908186550570E-09

    assert record.orbit_data.IDOT == 5.371652322309E-10
    assert record.orbit_data.l2_channel_codes == 1.000000000000E+00
    assert record.orbit_data.GPS_Week_no == 2.229000000000E+03
    assert record.orbit_data.L2_P_flag == 0.000000000000E+00

    assert record.orbit_data.SV_accuracy == 4.000000000000E+00
    assert record.orbit_data.SV_health == 0.000000000000E+00
    assert record.orbit_data.TGD == 1.862645149231E-09
    assert record.orbit_data.IODC == 5.500000000000E+01

    assert record.orbit_data.transmission_time == 3.817800000000E+05
    assert record.orbit_data.fit_interval == 4.000000000000E+00


### V4 ###

def test_GPSLNAVRecord_read_epoch_line():
    record = GPSLNAVRecord("SV")
    record.read_epoch_line("G03 2022 09 29 12 00 00-3.581880591810e-04-5.115907697473e-12 0.000000000000e+00")
    assert record.timestamp == "2022-09-29T12:00:00"
    assert record.clock_bias == -3.581880591810e-04
    assert record.clock_drift == -5.115907697473e-12
    assert record.clock_drift_rate == 0.000000000000e+00


def test_GPSLNAVRecord_read_lines():
    record = GPSLNAVRecord("SV")
    record.read_lines(
        list(map(lambda s: normalize_data_string(s),
                 [
                     "     5.500000000000E+01 1.612500000000E+01 4.391254341941E-09 1.650293527635E+00",
                     "     7.506459951401E-07 4.497775575146E-03 8.512288331985E-06 5.153542041779E+03",
                     "     3.888000000000E+05-1.247972249985E-07 1.397849200567E+00-1.862645149231E-09",
                     "     9.751815851645E-01 2.221875000000E+02 1.064872642026E+00-7.908186550570E-09",
                     "     5.371652322309E-10 1.000000000000E+00 2.229000000000E+03 0.000000000000E+00",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     3.817800000000E+05 4.000000000000E+00"
                 ]))
    )
    assert record.orbit_data.IODE == 5.500000000000E+01
    assert record.orbit_data.C_rs == 1.612500000000E+01
    assert record.orbit_data.Delta_n == 4.391254341941E-09
    assert record.orbit_data.M0 == 1.650293527635E+00

    assert record.orbit_data.C_uc == 7.506459951401E-07
    assert record.orbit_data.e == 4.497775575146E-03
    assert record.orbit_data.C_us == 8.512288331985E-06
    assert record.orbit_data.sqrt_A == 5.153542041779E+03

    assert record.orbit_data.T_oe == 3.888000000000E+05
    assert record.orbit_data.C_ic == -1.247972249985E-07
    assert record.orbit_data.OMEGA0 == 1.397849200567E+00
    assert record.orbit_data.C_is == -1.862645149231E-09

    assert record.orbit_data.i0 == 9.751815851645E-01
    assert record.orbit_data.C_rc == 2.221875000000E+02
    assert record.orbit_data.omega == 1.064872642026E+00
    assert record.orbit_data.OMEGA_DOT == -7.908186550570E-09

    assert record.orbit_data.IDOT == 5.371652322309E-10
    assert record.orbit_data.L2_channel_codes == 1.000000000000E+00
    assert record.orbit_data.GPS_Week_no == 2.229000000000E+03
    assert record.orbit_data.L2_P_flag == 0.000000000000E+00

    assert record.orbit_data.SV_accuracy == 4.000000000000E+00
    assert record.orbit_data.SV_health == 0.000000000000E+00
    assert record.orbit_data.TGD == 1.862645149231E-09
    assert record.orbit_data.IODC == 5.500000000000E+01

    assert record.orbit_data.t_tm == 3.817800000000E+05
    assert record.orbit_data.fit_interval == 4.000000000000E+00


def test_GPSCNAVRecord_read_epoch_line():
    record = GPSCNAVRecord("SV")
    record.read_epoch_line("G03 2022 09 29 12 00 00-3.581880591810e-04-5.115907697473e-12 0.000000000000e+00")
    assert record.timestamp == "2022-09-29T12:00:00"
    assert record.clock_bias == -3.581880591810e-04
    assert record.clock_drift == -5.115907697473e-12
    assert record.clock_drift_rate == 0.000000000000e+00


def test_GPSCNAVRecord_read_lines():
    record = GPSCNAVRecord("SV")
    record.read_lines(
        list(map(lambda s: normalize_data_string(s),
                 [
                     "     5.500000000000E+01 1.612500000000E+01 4.391254341941E-09 1.650293527635E+00",
                     "     7.506459951401E-07 4.497775575146E-03 8.512288331985E-06 5.153542041779E+03",
                     "     3.888000000000E+05-1.247972249985E-07 1.397849200567E+00-1.862645149231E-09",
                     "     9.751815851645E-01 2.221875000000E+02 1.064872642026E+00-7.908186550570E-09",
                     "     5.371652322309E-10 1.000000000000E+00 2.229000000000E+03 0.000000000000E+00",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     3.817800000000E+05 4.000000000000E+00"
                 ]))
    )
    assert record.orbit_data.A_DOT == 5.500000000000E+01
    assert record.orbit_data.C_rs == 1.612500000000E+01
    assert record.orbit_data.Delta_n0 == 4.391254341941E-09
    assert record.orbit_data.M0 == 1.650293527635E+00

    assert record.orbit_data.C_uc == 7.506459951401E-07
    assert record.orbit_data.e == 4.497775575146E-03
    assert record.orbit_data.C_us == 8.512288331985E-06
    assert record.orbit_data.sqrt_A == 5.153542041779E+03

    assert record.orbit_data.t_op == 3.888000000000E+05
    assert record.orbit_data.C_ic == -1.247972249985E-07
    assert record.orbit_data.OMEGA0 == 1.397849200567E+00
    assert record.orbit_data.C_is == -1.862645149231E-09

    assert record.orbit_data.i0 == 9.751815851645E-01
    assert record.orbit_data.C_rc == 2.221875000000E+02
    assert record.orbit_data.omega == 1.064872642026E+00
    assert record.orbit_data.OMEGA_DOT == -7.908186550570E-09

    assert record.orbit_data.IDOT == 5.371652322309E-10
    assert record.orbit_data.Delta_n0_dot == 1.000000000000E+00
    assert record.orbit_data.URAI_NED0 == 2.229000000000E+03
    assert record.orbit_data.URAI_NED1 == 0.000000000000E+00

    assert record.orbit_data.URAI_ED == 4.000000000000E+00
    assert record.orbit_data.SV_health == 0.000000000000E+00
    assert record.orbit_data.TGD == 1.862645149231E-09
    assert record.orbit_data.URAI_NED2 == 5.500000000000E+01

    assert record.orbit_data.ISC_L1CA == 4.000000000000E+00
    assert record.orbit_data.ISC_L2C == 0.000000000000E+00
    assert record.orbit_data.ISC_L5I5 == 1.862645149231E-09
    assert record.orbit_data.ISC_L5Q5 == 5.500000000000E+01

    assert record.orbit_data.t_tm == 3.817800000000E+05
    assert record.orbit_data.wn_op == 4.000000000000E+00


def test_GPSCNAV2Record_read_epoch_line():
    record = GPSCNAV2Record("SV")
    record.read_epoch_line("G03 2022 09 29 12 00 00-3.581880591810e-04-5.115907697473e-12 0.000000000000e+00")
    assert record.timestamp == "2022-09-29T12:00:00"
    assert record.clock_bias == -3.581880591810e-04
    assert record.clock_drift == -5.115907697473e-12
    assert record.clock_drift_rate == 0.000000000000e+00


def test_GPSCNAV2Record_read_lines():
    record = GPSCNAV2Record("SV")
    record.read_lines(
        list(map(lambda s: normalize_data_string(s),
                 [
                     "     5.500000000000E+01 1.612500000000E+01 4.391254341941E-09 1.650293527635E+00",
                     "     7.506459951401E-07 4.497775575146E-03 8.512288331985E-06 5.153542041779E+03",
                     "     3.888000000000E+05-1.247972249985E-07 1.397849200567E+00-1.862645149231E-09",
                     "     9.751815851645E-01 2.221875000000E+02 1.064872642026E+00-7.908186550570E-09",
                     "     5.371652322309E-10 1.000000000000E+00 2.229000000000E+03 0.000000000000E+00",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     4.000000000000E+00 0.000000000000E+00 1.862645149231E-09 5.500000000000E+01",
                     "     4.000000000000E+00 0.000000000000E+00",
                     "     3.817800000000E+05 4.000000000000E+00"
                 ]))
    )
    assert record.orbit_data.A_DOT == 5.500000000000E+01
    assert record.orbit_data.C_rs == 1.612500000000E+01
    assert record.orbit_data.Delta_n0 == 4.391254341941E-09
    assert record.orbit_data.M0 == 1.650293527635E+00

    assert record.orbit_data.C_uc == 7.506459951401E-07
    assert record.orbit_data.e == 4.497775575146E-03
    assert record.orbit_data.C_us == 8.512288331985E-06
    assert record.orbit_data.sqrt_A == 5.153542041779E+03

    assert record.orbit_data.t_op == 3.888000000000E+05
    assert record.orbit_data.C_ic == -1.247972249985E-07
    assert record.orbit_data.OMEGA0 == 1.397849200567E+00
    assert record.orbit_data.C_is == -1.862645149231E-09

    assert record.orbit_data.i0 == 9.751815851645E-01
    assert record.orbit_data.C_rc == 2.221875000000E+02
    assert record.orbit_data.omega == 1.064872642026E+00
    assert record.orbit_data.OMEGA_DOT == -7.908186550570E-09

    assert record.orbit_data.IDOT == 5.371652322309E-10
    assert record.orbit_data.Delta_n0_dot == 1.000000000000E+00
    assert record.orbit_data.URAI_NED0 == 2.229000000000E+03
    assert record.orbit_data.URAI_NED1 == 0.000000000000E+00

    assert record.orbit_data.URAI_ED == 4.000000000000E+00
    assert record.orbit_data.SV_health == 0.000000000000E+00
    assert record.orbit_data.TGD == 1.862645149231E-09
    assert record.orbit_data.URAI_NED2 == 5.500000000000E+01

    assert record.orbit_data.ISC_L1CA == 4.000000000000E+00
    assert record.orbit_data.ISC_L2C == 0.000000000000E+00
    assert record.orbit_data.ISC_L5I5 == 1.862645149231E-09
    assert record.orbit_data.ISC_L5Q5 == 5.500000000000E+01

    assert record.orbit_data.ISC_L1Cd == 4.000000000000E+00
    assert record.orbit_data.ISC_L1Cp == 0.000000000000E+00

    assert record.orbit_data.t_tm == 3.817800000000E+05
    assert record.orbit_data.wn_op == 4.000000000000E+00
