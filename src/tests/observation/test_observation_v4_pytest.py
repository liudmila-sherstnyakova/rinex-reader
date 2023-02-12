import reader
from tests import resources_path


def test_read_obs_v4__no_filters():
    result = reader.read_rinex_file(rinex_file_path=resources_path/"observation_v4.22o")
    assert result.data.satellites.keys() == {'C05', 'C06', 'C09', 'C11', 'C12', 'C16', 'C19', 'C21', 'C22', 'C34',
                                             'C36', 'E03', 'E05', 'E09', 'E15', 'E34', 'G01', 'G03', 'G04', 'G06',
                                             'G09', 'G11', 'G19', 'G31', 'R02', 'R03', 'R04', 'R11', 'R12', 'R13',
                                             'R18', 'R19', 'R20', 'E13', 'E31'}
    assert result.data.satellites["C11"].keys() == {'2022-09-29T11:00:00', '2022-09-29T11:00:10', '2022-09-29T11:00:20', '2022-09-29T11:00:30'}
    assert result.data.satellites["E31"].keys() == {'2022-09-29T11:00:30'}
    # assert all fields for E34 at 2022-09-29T11:00:00
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C1X"]["value"] == 24449838.900
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C1X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C1X"]["ssi"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L1X"]["value"] == 128484758.655
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L1X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L1X"]["ssi"] == 8
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D1X"]["value"] == -1514.702
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D1X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D1X"]["ssi"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C5X"]["value"] == 24449845.760
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C5X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["C5X"]["ssi"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L5X"]["value"] == 95946424.903
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L5X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["L5X"]["ssi"] == 1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D5X"]["value"] == -1131.108
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D5X"]["lli"] == -1
    assert result.data.satellites["E34"]['2022-09-29T11:00:00']["D5X"]["ssi"] == -1


def test_read_obs_v4__gnss_filter():
    result = reader.read_rinex_file(
        rinex_file_path=resources_path/"observation_v4.22o",
        gnss=["R", "C"]
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'R', 'C'}


def test_read_obs_v4__obs_types_filter():
    # using list as filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v4.22o",
        obs_types=['C5X', 'L5X'],
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'E'}  # Only E defines C5X, L5X

    # using regex as filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v4.22o",
        obs_types=".5.",  # all obs types with 5 in the middle
    )
    assert {k[0] for k in result.data.satellites.keys()} == {'C', 'E'}  # Only E and C defines .5. types


def test_read_obs_v4__time_filter():
    # using only single start time filter
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v4.22o",
        start_epoch="2022-09-29T11:00:10"
    )
    assert len(result.data.satellites) == 34
    for sv in result.data.satellites.values():
        assert sv.keys() == {"2022-09-29T11:00:10"}

    # using both start and end time filters
    result = reader.read_rinex_file(
        rinex_file_path=resources_path / "observation_v4.22o",
        start_epoch="2022-09-29T11:0:10",
        end_epoch="2022-09-29T11:00:20"
    )
    assert len(result.data.satellites) == 34
    for sv in result.data.satellites.values():
        assert sv.keys() == {'2022-09-29T11:00:10', '2022-09-29T11:00:20'}
