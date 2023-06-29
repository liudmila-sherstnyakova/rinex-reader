from nmbu.rinex import reader
from tests import resources_path


def test_read_obs_v3__no_filters():
    result = reader.read_rinex_file(rinex_file_path=resources_path / "observation_v3.22o")
    assert result.data.satellites.keys() == {'C11', 'C12', 'C19', 'C21', 'C22', 'C34', 'C36', 'E03', 'E05', 'E09',
                                             'E15', 'E34', 'G03', 'G04', 'G06', 'G09', 'G17', 'G19', 'R02', 'R03',
                                             'R04', 'R13', 'R18', 'R19', 'R20', 'C05', 'C27', 'C29', 'C30', 'E07',
                                             'E24', 'E26', 'E31', 'E33', 'G08', 'G10', 'G16', 'G18', 'G21', 'G23',
                                             'G27', 'R01', 'R15', 'R17', 'R23', 'R24'}
    assert result.data.satellites["C11"].keys() == {'2022-09-29T11:00:00', '2022-09-29T11:00:10', '2022-09-29T11:00:20'}
    assert result.data.satellites["R17"].keys() == {'2022-09-30T04:59:40', '2022-09-30T04:59:50'}
    # assert all fields for E03 at 2022-09-29T11:00:00
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C1X"]["value"] == 25790898.320
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C1X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C1X"]["ssi"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L1X"]["value"] == 135532114.919
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L1X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L1X"]["ssi"] == 7
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D1X"]["value"] == 2768.707
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D1X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D1X"]["ssi"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C5X"]["value"] == 25790905.960
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C5X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["C5X"]["ssi"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L5X"]["value"] == 101209101.998
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L5X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["L5X"]["ssi"] == 7
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D5X"]["value"] == 2067.541
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D5X"]["lli"] == -1
    assert result.data.satellites["E03"]['2022-09-29T11:00:00']["D5X"]["ssi"] == -1


def test_read_obs_v3__gnss_filter():
    result = reader.read_rinex_file(
        rinex_file_path=resources_path/"observation_v3.22o",
        gnss=["R", "C"]
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'R', 'C'}


def test_read_obs_v3__obs_types_filter():
    # using list as filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v3.22o",
        obs_types=['C5X', 'L5X'],
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'E'}  # Only E defines C5X, L5X

    # using regex as filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v3.22o",
        obs_types=".5.",  # all obs types with 5 in the middle
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'C', 'E'}  # Only E and C defines .5. types


def test_read_obs_v3__time_filter():
    # using only single start time filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v3.22o",
        start_epoch="2022-09-29T11:00:00"
    )
    assert len(result.data.satellites) == 25
    for sv in result.data.satellites.values():
        assert sv.keys() == {"2022-09-29T11:00:00"}

    # using both start and end time filters
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v3.22o",
        start_epoch="2022-09-29T11:00:00",
        end_epoch="2022-09-29T11:00:20"
    )
    assert len(result.data.satellites) == 25
    for sv in result.data.satellites.values():
        assert sv.keys() == {'2022-09-29T11:00:00', '2022-09-29T11:00:10', '2022-09-29T11:00:20'}

def test_read_obs_v3__single_sv():
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v3_single_sv.22o"
    )
    assert len(result.data.satellites) == 1
    assert result.data.satellites["C12"]["2022-09-29T11:00:00"]["C2I"]["value"] == 23486627.58
    assert result.data.satellites["C12"]["2022-09-29T11:00:00"]["D7I"]["value"] == -1501.578