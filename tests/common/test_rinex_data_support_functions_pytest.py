from nmbu.rinex import reader
from nmbu.rinex.navigation.v3.nav_message_type.GAL import GALNavRecordOrbitData as GALNavRecordOrbitDataV3
from nmbu.rinex.navigation.v4.nav_message_type.GAL_INAV_FNAV import GALNavRecordOrbitData as GALNavRecordOrbitDataV4
from tests import resources_path


def test_find_closest_match():
    rinex_nav_v3 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v3.22p")
    e05 = rinex_nav_v3.find_closest_match(sv="E05", timestamp="2022-09-29T10:00:00")
    assert isinstance(e05, GALNavRecordOrbitDataV3)
    assert e05.omega == 1.470263377777
    e06 = rinex_nav_v3.find_closest_match(sv="E06", timestamp="2022-09-29T10:00:00")
    assert e06 is None

    rinex_nav_v4 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v4.22p")
    e09 = rinex_nav_v4.find_closest_match(sv="E09", timestamp="2022-09-29T10:00:00")
    assert isinstance(e09, GALNavRecordOrbitDataV4)
    assert e09.SV_health == 3.12
    e06 = rinex_nav_v4.find_closest_match(sv="E06", timestamp="2022-09-29T10:00:00")
    assert e06 is None
