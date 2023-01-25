from typing import IO

import numpy as np

import common
from gnss import get_correct_gnss, GNSS, Mixed

RINEX_VERSION_TYPE_LABEL = "RINEX VERSION / TYPE"
MARKER_NAME_LABEL = "MARKER NAME"
ANTENNA_NO_TYPE_LABEL = "ANT # / TYPE"
ANTENNA_DELTA_HEN_LABEL = "ANTENNA: DELTA H/E/N"
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
        return "{no:s} ({type:s}) | Height: {h:.4f}, Eccentricity: E: {e:.4f}, N: {n:.4f}".format(no=self.number,
                                                                                                  type=self.type,
                                                                                                  h=self.height,
                                                                                                  e=self.east,
                                                                                                  n=self.north)


class Header:

    def __init__(self):
        self.version = 0.0
        self.time_of_first_observation: np.datetime64 = None
        self.gnss_systems: [GNSS] = []
        self.file_type: str = None  # O | N | M
        self.mixed_gnss: bool = None
        self.system_time = None
        self.antenna = Antenna()
        self.marker_name = None
        self.approximate_position = {}
        self.other = {}

    def obs_types_for_gnss(self, gnss_symbol: str) -> GNSS:
        for gnss in self.gnss_systems:
            if gnss.symbol == gnss_symbol:
                return gnss

    def __str__(self):
        return "RINEX FILE \n" \
               "VERSION: " + self.version.__str__() + "\n" \
               "TYPE: " + self.file_type + "\n" \
               "MIXED: " + self.mixed_gnss.__str__() + "\n" \
               "GNSS SYSTEMS: " + self.gnss_systems.__str__() + "\n" \
               "SYSTEM TIME: " + self.system_time + "\n" \
               "TIME OF FIRST OBSERVATION: " + self.time_of_first_observation.__str__() + "\n" \
               "MARKER: " + self.marker_name + "\n" \
               "ANTENNA: " + self.antenna.__str__() + "\n" \
               "APPROXIMATE POSITION: " + self.approximate_position.__str__() + "\n" \
               "" + '\n'.join(': '.join((key, val)) for (key, val) in self.other.items()) # all unnecessary data from header


def read_header_block(file: IO, version: float, file_type: str, gnss: GNSS) -> Header:
    """

    :param file:
    :param version:
    :param file_type:
    :param gnss:
    :return:
    """
    header = Header()
    header.version = version
    header.file_type = file_type

    if isinstance(gnss, Mixed):
        header.mixed_gnss = True
    else:
        header.mixed_gnss = False
        header.gnss_systems.append(gnss)

    for line in file:
        if line.__contains__(END_OF_HEADER_LABEL):
            break

        elif line.__contains__(MARKER_NAME_LABEL):
            header.marker_name = line[:60].strip()
        elif line.__contains__(ANTENNA_NO_TYPE_LABEL):
            header.antenna.number = line[:20].strip()
            header.antenna.type = line[20:40].strip()
        elif line.__contains__(ANTENNA_DELTA_HEN_LABEL):
            header.antenna.height = common.str2float(line[:14],
                                                     "Invalid antenna delta height in " + ANTENNA_DELTA_HEN_LABEL)
            header.antenna.east = common.str2float(line[14:28],
                                                   "Invalid antenna delta east in " + ANTENNA_DELTA_HEN_LABEL)
            header.antenna.north = common.str2float(line[28:42],
                                                    "Invalid antenna delta north in " + ANTENNA_DELTA_HEN_LABEL)
        elif line.__contains__(APPROXIMATE_POSITION_LABEL):
            header.approximate_position["X"] = common.str2float(line[:14],
                                                                "Invalid X coordinate in " + APPROXIMATE_POSITION_LABEL)
            header.approximate_position["Y"] = common.str2float(line[14:28],
                                                                "Invalid Y coordinate in " + APPROXIMATE_POSITION_LABEL)
            header.approximate_position["Z"] = common.str2float(line[28:42],
                                                                "Invalid Z coordinate in " + APPROXIMATE_POSITION_LABEL)
        elif line.__contains__(SYS_NO_OBS_TYPES_LABEL):
            system = get_correct_gnss(line[0]) if header.mixed_gnss and line[0] != ' ' else None

            if system is not None:  # continue reading previous system
                system.obs_types += line[7:60].strip().split()
                header.gnss_systems.append(system)
            else:
                header.gnss_systems[-1].obs_types += line[7:60].strip().split()
        elif line.__contains__(TIME_OF_FIRST_OBS_LABEL):
            year = common.str2int(line[0:6], "Invalid year value in " + TIME_OF_FIRST_OBS_LABEL)
            month = common.str2int(line[6:12], "Invalid month value in " + TIME_OF_FIRST_OBS_LABEL)
            day = common.str2int(line[12:18], "Invalid date value in " + TIME_OF_FIRST_OBS_LABEL)
            hour = common.str2int(line[18:24], "Invalid hour value in " + TIME_OF_FIRST_OBS_LABEL)
            minute = common.str2int(line[24:30], "Invalid minute value in " + TIME_OF_FIRST_OBS_LABEL)
            full_seconds = common.str2int(line[30:35], "Invalid seconds value in " + TIME_OF_FIRST_OBS_LABEL)
            # RINEX uses 7 decimals for seconds value, meaning that the lowest digit is 100 nanoseconds
            nanoseconds = common.str2int(line[36:43], "Invalid nanoseconds value in " + TIME_OF_FIRST_OBS_LABEL) * 100
            start_time = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{seconds:02d}".format(year=year, month=month,
                                                                                                 day=day, hour=hour,
                                                                                                 minute=minute,
                                                                                                 seconds=full_seconds)
            header.time_of_first_observation = np.datetime64(start_time) + np.timedelta64(nanoseconds, 'ns')
            header.system_time = line[48:51] if header.mixed_gnss else header.gnss_systems[0].name
        else:
            label = line[60:80].strip()
            if label in header.other.keys():
                header.other[label] += " | " + line[:60].strip()
            else:
                header.other[label] = line[:60].strip()
        # end of for loop
    return header
