
import numpy

from nmbu.rinex.observation.v3.header import read_observation_header_v3
from nmbu.rinex.observation.v4.header import read_observation_header_v4
from tests import resources_path


def test_read_navigation_header_v3():
    with (resources_path/"header_v3.22o").open() as f:
        first_line = next(f)  # simulate reading first line
        result = read_observation_header_v3(file=f, version=3.05, file_type='O', gnss='M')
        assert result.version == 3.05
        assert result.file_type == 'O'
        assert result.gnss == 'M'
        assert result.marker_name == 'K004'
        assert result.antenna.east == 0
        assert result.antenna.north == 0
        assert result.antenna.height == 1.3142
        assert result.antenna.number == '1451-12216'
        assert result.antenna.type == 'TPSHIPER_VR     NONE'
        assert result.approximate_position["X"] == 3172507.4901
        assert result.approximate_position["Y"] == 603208.4428
        assert result.approximate_position["Z"] == 5481884.1614
        assert result.obs_types.keys() == {'G', 'R', 'E', 'C'}
        assert result.obs_types['G'] == ['C1C', 'L1C', 'D1C', 'C1W', 'L1W', 'D1W', 'C1X', 'L1X', 'D1X', 'C1Y', 'L1Y', 'D1Y', 'C1Z', 'C2C', 'L2C', 'D2C', 'C2W', 'L2W', 'D2W', 'C2X', 'L2X', 'D2X', 'C2Y', 'L2Y', 'D2Y', 'C2Z', 'C3C']
        assert result.obs_types['R'] == ['C1C', 'L1C', 'D1C', 'C2C', 'L2C', 'D2C']
        assert result.obs_types['E'] == ['C1X', 'L1X', 'D1X', 'C5X', 'L5X', 'D5X']
        assert result.obs_types['C'] == ['C2I', 'L2I', 'D2I', 'C5P', 'L5P', 'D5P', 'C7I', 'L7I', 'D7I']
        assert result.time_of_first_observation == numpy.datetime64('2022-09-29T11:00:00.000000000')
        assert result.system_time == 'GPS'
        assert len(result.other) == 12
        assert result.other.keys() == {'PGM / RUN BY / DATE', 'COMMENT', 'OBSERVER / AGENCY', 'REC # / TYPE / VERS', 'TIME OF LAST OBS', 'INTERVAL', '# OF SATELLITES', 'PRN / # OF OBS', 'SYS / PHASE SHIFT', 'GLONASS SLOT / FRQ #', 'GLONASS COD/PHS/BIS', 'LEAP SECONDS'}


def test_read_navigation_header_v4():
    with (resources_path/"header_v4.22o").open() as f:
        first_line = next(f)  # simulate reading first line
        result = read_observation_header_v4(file=f, version=4.00, file_type='O', gnss='M')
        assert result.version == 4.00
        assert result.file_type == 'O'
        assert result.gnss == 'M'
        assert result.marker_name == 'SSIR'
        assert result.antenna.east == 0
        assert result.antenna.north == 0
        assert result.antenna.height == 1.2886
        assert result.antenna.number == '1451-12132'
        assert result.antenna.type == 'TPSHIPER_VR'
        assert result.approximate_position["X"] == 3172370.6788
        assert result.approximate_position["Y"] == 603854.2750
        assert result.approximate_position["Z"] == 5481905.3621
        assert result.obs_types.keys() == {'G', 'R', 'E', 'C'}
        assert result.obs_types['G'] == ['C1C', 'L1C', 'D1C', 'C1W', 'L1W', 'D1W', 'C2W', 'L2W', 'D2W']
        assert result.obs_types['R'] == ['C1C', 'L1C', 'D1C', 'C2C', 'L2C', 'D2C']
        assert result.obs_types['E'] == ['C1X', 'L1X', 'D1X', 'C5X', 'L5X', 'D5X']
        assert result.obs_types['C'] == ['C2I', 'L2I', 'D2I', 'C5P', 'L5P', 'D5P', 'C7I', 'L7I', 'D7I']
        assert result.time_of_first_observation == numpy.datetime64('2022-09-29T11:00:00.000000000')
        assert result.system_time == 'GPS'
        assert len(result.other) == 10
        assert result.other.keys() == {'PGM / RUN BY / DATE', 'COMMENT', 'OBSERVER / AGENCY', 'REC # / TYPE / VERS', 'TIME OF LAST OBS', 'INTERVAL', '# OF SATELLITES', 'PRN / # OF OBS', 'GLONASS SLOT / FRQ #', 'LEAP SECONDS'}


