import numpy as np
import common
from gnss import get_correct_gnss, GNSS, Mixed

RINEX_VERSION_TYPE_LABEL = "RINEX VERSION / TYPE"
MARKER_NAME_LABEL = "MARKER NAME"
ANTENNA_NO_TYPE_LABEL = "ANT # / TYPE"
ANTENNA_DELTA_HEN_LABEL = "ANTENNA: DELTA H/E/N"  # TODO
APPROXIMATE_POSITION_LABEL = "APPROX POSITION XYZ"
SYS_NO_OBS_TYPES_LABEL = "SYS / # / OBS TYPES"
TIME_OF_FIRST_OBS_LABEL = "TIME OF FIRST OBS"
END_OF_HEADER_LABEL = "END OF HEADER"


class Antenna:
    def __init__(self):
        self.number = None
        self.type = None
        self.height = None
        self.east = None
        self.north = None

    def __repr__(self):
        return "{no:s} ({type:s}) | Height: {h:f}, Eccentricity: E: {e:f}, N: {n:f}".format(no=self.number,
                                                                                                type=self.type,
                                                                                                h=self.height,
                                                                                                e=self.east,
                                                                                                n=self.north)


# parses 'RINEX VERSION / TYPE' line
#      3.05           OBSERVATION DATA    MIXED               RINEX VERSION / TYPE
class Header:

    def __init__(self, first_line: str):
        # self.obs_types_per_gnss = []
        self.time_of_first_observation: np.datetime64 = None
        self.gnss_systems: [GNSS] = []
        self.file_type: str = None # O | N | M
        self.mixed_gnss: bool = None
        self.system_time = None
        self.antenna = Antenna()
        self.marker_name = None
        self.approximate_position = {}
        self.other = {}

        label = first_line[60:80]
        assert label == RINEX_VERSION_TYPE_LABEL

        self.version = common.str2float(first_line[0:9], "Invalid version value in " + RINEX_VERSION_TYPE_LABEL)
        self.file_type = first_line[20]

        gnss_system = get_correct_gnss(first_line[40])
        if isinstance(gnss_system, Mixed):
            self.mixed_gnss = True
        else:
            self.mixed_gnss = False
            self.gnss_systems.append(gnss_system)

    def read_line(self, line: str) -> bool:
        """
        Read single line from RINEX file header and parse it according to format specification

        Returns True if 'END OF HEADER' label is received and False otherwise.
        """
        if line.__contains__(MARKER_NAME_LABEL):
            self.marker_name = line[:60].strip()
        elif line.__contains__(ANTENNA_NO_TYPE_LABEL):
            self.antenna.number = line[:20].strip()
            self.antenna.type = line[20:40].strip()
        elif line.__contains__(ANTENNA_DELTA_HEN_LABEL):
            self.antenna.height = common.str2float(line[:14],
                                                   "Invalid antenna delta height in " + ANTENNA_DELTA_HEN_LABEL)
            self.antenna.east = common.str2float(line[14:28],
                                                 "Invalid antenna delta east in " + ANTENNA_DELTA_HEN_LABEL)
            self.antenna.north = common.str2float(line[28:42],
                                                  "Invalid antenna delta north in " + ANTENNA_DELTA_HEN_LABEL)
        elif line.__contains__(APPROXIMATE_POSITION_LABEL):
            self.approximate_position["X"] = common.str2float(line[:14],
                                                              "Invalid X coordinate in " + APPROXIMATE_POSITION_LABEL)
            self.approximate_position["Y"] = common.str2float(line[14:28],
                                                              "Invalid Y coordinate in " + APPROXIMATE_POSITION_LABEL)
            self.approximate_position["Z"] = common.str2float(line[28:42],
                                                              "Invalid Z coordinate in " + APPROXIMATE_POSITION_LABEL)
        elif line.__contains__(SYS_NO_OBS_TYPES_LABEL):
            system = get_correct_gnss(line[0]) if self.mixed_gnss and line[0] != ' ' else None

            if system is not None:  # continue reading previous system
                system.obs_types += line[7:60].strip().split()
                self.gnss_systems.append(system)
            else:
                self.gnss_systems[-1].obs_types += line[7:60].strip().split()
        elif line.__contains__(TIME_OF_FIRST_OBS_LABEL):
            year = common.str2int(line[0:6], "Invalid year value in " + TIME_OF_FIRST_OBS_LABEL)
            month = common.str2int(line[6:12], "Invalid month value in " + TIME_OF_FIRST_OBS_LABEL)
            day = common.str2int(line[12:18], "Invalid date value in " + TIME_OF_FIRST_OBS_LABEL)
            hour = common.str2int(line[18:24], "Invalid hour value in " + TIME_OF_FIRST_OBS_LABEL)
            minute = common.str2int(line[24:30], "Invalid minute value in " + TIME_OF_FIRST_OBS_LABEL)
            full_seconds = common.str2int(line[30:35], "Invalid seconds value in " + TIME_OF_FIRST_OBS_LABEL)
            # RINEX uses 7 decimals for seconds value, meaning that the lowest digit is 100 nanoseconds
            nanoseconds = common.str2int(line[36:43], "Invalid nanoseconds value in " + TIME_OF_FIRST_OBS_LABEL) * 100
            st = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{seconds:02d}".format(year=year, month=month,
                                                                                                 day=day, hour=hour,
                                                                                                 minute=minute,
                                                                                                 seconds=full_seconds)
            self.time_of_first_observation = np.datetime64(st) + np.timedelta64(nanoseconds, 'ns')
            self.system_time = line[48:51] if self.mixed_gnss else self.gnss_systems[0].name
        elif line.__contains__(END_OF_HEADER_LABEL):
            return True
        else:
            label = line[60:80].strip()
            if label in self.other.keys():
                self.other[label] += " | " + line[:60].strip()
            else:
                self.other[label] = line[:60].strip()
        return False

    def obs_types_for_gnss(self, gnss_symbol: str) -> GNSS:
        for gnss in self.gnss_systems:
            if gnss.symbol == gnss_symbol:
                return gnss

    def __repr__(self):
        return "RINEX FILE \n" \
               "VERSION: " + self.version.__repr__() + "\n" \
               "TYPE: " + self.file_type + "\n" \
               "MIXED: " + self.mixed_gnss.__repr__() + "\n" \
               "GNSS SYSTEMS: " + self.gnss_systems.__repr__() + "\n" \
               "SYSTEM TIME: " + self.system_time + "\n" \
               "TIME OF FIRST OBSERVATION: " + self.time_of_first_observation.__str__() + "\n" \
               "MARKER: " + self.marker_name + "\n" \
               "ANTENNA: " + self.antenna.__str__() + "\n" \
               "" + APPROXIMATE_POSITION_LABEL + ": " + self.approximate_position.__str__() + "\n" \
               "" + '\n'.join(': '.join((key, val)) for (key, val) in self.other.items())
