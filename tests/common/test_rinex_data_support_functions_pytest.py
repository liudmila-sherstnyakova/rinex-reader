from nmbu.rinex import reader
from nmbu.rinex.navigation.v3.nav_message_type.GAL import GALNavRecordOrbitData as GALNavRecordOrbitDataV3
from nmbu.rinex.navigation.v4.nav_message_type.GAL_INAV_FNAV import GALNavRecordOrbitData as GALNavRecordOrbitDataV4
from nmbu.rinex.navigation.v4.nav_message_type.ION_Klobuchar import IONKlobNavRecordData
from tests import resources_path


def test_find_closest_match():
    rinex_nav_v3 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v3.22p")
    e05 = rinex_nav_v3.find_closest_match(sv="E05", timestamp="2022-09-29T10:00:00")
    assert isinstance(e05, GALNavRecordOrbitDataV3)
    assert e05.omega == 1.470263377777
    assert e05.timestamp == "2022-09-29T09:50:00"
    e06 = rinex_nav_v3.find_closest_match(sv="E06", timestamp="2022-09-29T10:00:00")
    assert e06 is None

    rinex_nav_v4 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v4.22p")
    e09 = rinex_nav_v4.find_closest_match(sv="E09", timestamp="2022-09-29T10:00:00")
    assert isinstance(e09, GALNavRecordOrbitDataV4)
    assert e09.SV_health == 3.12
    assert e09.timestamp == "2022-09-29T09:20:00"
    e06 = rinex_nav_v4.find_closest_match(sv="E06", timestamp="2022-09-29T10:00:00")
    assert e06 is None

def test_find_closest_correction_match():
    rinex_nav_v3 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v3.22p")
    e05 = rinex_nav_v3.find_closest_correction_match(correction_type='ION', sv="E05", timestamp="2022-09-29T10:00:00")
    assert e05 is None # No ION block in RINEX 3

    rinex_nav_v4 = reader.read_rinex_file(rinex_file_path=resources_path / "navigation_v4.22p")
    c06_ion = rinex_nav_v4.find_closest_correction_match(correction_type='ION', sv="C06", timestamp="2022-09-29T10:00:00")
    assert isinstance(c06_ion, IONKlobNavRecordData)
    assert c06_ion.Alpha0 == 2.421438694e-08
    assert c06_ion.Alpha1 == 2.682209014893e-07
    assert c06_ion.Alpha2 == -2.026557922363e-06
    assert c06_ion.Alpha3 == 2.98023223877e-06
    assert c06_ion.Beta0 == 151552.0
    assert c06_ion.Beta1 == -802816.0
    assert c06_ion.Beta2 == 4128768.0
    assert c06_ion.Beta3 == -2490368.0
    assert c06_ion.timestamp == "2022-09-29T09:40:42"
    e06 = rinex_nav_v4.find_closest_correction_match(correction_type='ION', sv="E06", timestamp="2022-09-29T10:00:00")
    assert e06 is None # No ION block for E06
