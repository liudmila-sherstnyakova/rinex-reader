#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import IO, Dict

import numpy as np

from nmbu.rinex.common import *


class Antenna:
    def __init__(self):
        self.number: str = ""
        self.type: str = ""
        self.height: float = 0
        self.east: float = 0
        self.north: float = 0

    def __repr__(self):
        return "{no:s} ({type:s}) | Height: {h:.4f}, Eccentricity: E: {e:.4f}, N: {n:.4f}".format(no=self.number,
                                                                                                  type=self.type,
                                                                                                  h=self.height,
                                                                                                  e=self.east,
                                                                                                  n=self.north)


class ObservationHeaderV4:
    def __init__(self, version: float, file_type: str, gnss: str):
        self.antenna: Antenna = Antenna()
        self.approximate_position: Dict[str, float] = {}
        self.file_type: str = file_type
        self.gnss: str = gnss
        self.marker_name: str = ""
        self.obs_types: Dict[str, List[str]] = {}
        self.other: Dict[str, str] = {}
        self.system_time: str = ""
        self.time_of_first_observation: np.datetime64 = None
        self.version: float = version
        self.interval: float = 0

    def __str__(self):
        return "RINEX FILE \n" \
               "VERSION: " + str(self.version) + "\n" + \
               "TYPE: " + self.file_type + "\n" + \
               "GNSS: " + self.gnss + "\n" + \
               "OBS TYPES: " + str(self.obs_types) + "\n" + \
               "SYSTEM TIME: " + self.system_time + "\n" + \
               "TIME OF FIRST OBSERVATION: " + str(self.time_of_first_observation) + "\n" + \
               "INTERVAL: " + self.interval + "\n" + \
               "MARKER: " + self.marker_name + "\n" + \
               "ANTENNA: " + self.antenna.__str__() + "\n" + \
               "APPROXIMATE POSITION: " + str(self.approximate_position) + \
               "\n" + '\n'.join(': '.join((key, val)) for (key, val) in self.other.items())


def read_observation_header_v4(
        file: IO,
        version: float,
        file_type: str,
        gnss: str
) -> ObservationHeaderV4:
    """

    :param file: IO.
        Required. File iterator that reads file line by line.
        Position of this iterator is expected to be on the 'RINEX VERSION / TYPE' line.
    :param version: float.
        Required. Version of the provided RINEX document as obtained from the first header line.
    :param file_type: str.
        Required. RINEX file type (N or O) as obtained from the first header line.
    :param gnss: str.
        Required. GNSS of the RINEX file (Mixed or Single) as obtained from the first header line.
    :return: ObservationHeaderV4.
        Holder object for header data. See observation.v4.header.ObservationHeaderV4.
    """
    result = ObservationHeaderV4(version, file_type, gnss)

    for line in file:
        if line.__contains__(END_OF_HEADER_LABEL):
            break

        elif line.__contains__(MARKER_NAME_LABEL):
            result.marker_name = line[:60].strip()
        elif line.__contains__(ANTENNA_NO_TYPE_LABEL):
            result.antenna.number = line[:20].strip()
            result.antenna.type = line[20:40].strip()
        elif line.__contains__(ANTENNA_DELTA_HEN_LABEL):
            result.antenna.height = str2float(line[:14],
                                              "Invalid antenna delta height in " + ANTENNA_DELTA_HEN_LABEL)
            result.antenna.east = str2float(line[14:28],
                                            "Invalid antenna delta east in " + ANTENNA_DELTA_HEN_LABEL)
            result.antenna.north = str2float(line[28:42],
                                             "Invalid antenna delta north in " + ANTENNA_DELTA_HEN_LABEL)
        elif line.__contains__(APPROXIMATE_POSITION_LABEL):
            result.approximate_position["X"] = str2float(line[:14],
                                                         "Invalid X coordinate in " + APPROXIMATE_POSITION_LABEL)
            result.approximate_position["Y"] = str2float(line[14:28],
                                                         "Invalid Y coordinate in " + APPROXIMATE_POSITION_LABEL)
            result.approximate_position["Z"] = str2float(line[28:42],
                                                         "Invalid Z coordinate in " + APPROXIMATE_POSITION_LABEL)
        elif line.__contains__(INTERVAL_LABEL):
            result.interval = str2float(line[:60],
                                        "Invalid interval value in" + INTERVAL_LABEL)
        elif line.__contains__(SYS_NO_OBS_TYPES_LABEL):
            gnss = line[0]
            assert gnss in supported_gnss or gnss == ' ', \
                "Unknown GNSS in {label:s}: {gnss:s}".format(
                    label=SYS_NO_OBS_TYPES_LABEL,
                    gnss=gnss)

            obs_types_amount = str2int(line[3:6], "Invalid number of obs types in " + SYS_NO_OBS_TYPES_LABEL)
            amount_of_lines_for_current_gnss = (obs_types_amount // 13)  # max amount of obs types in one line

            result.obs_types[gnss] = line[7:60].strip().split()
            for obs_types_extra_line in [next(file) for _ in range(amount_of_lines_for_current_gnss)]:
                result.obs_types[gnss] += obs_types_extra_line[7:60].strip().split()
        elif line.__contains__(TIME_OF_FIRST_OBS_LABEL):
            year = str2int(line[0:6], "Invalid year value in " + TIME_OF_FIRST_OBS_LABEL)
            month = str2int(line[6:12], "Invalid month value in " + TIME_OF_FIRST_OBS_LABEL)
            day = str2int(line[12:18], "Invalid date value in " + TIME_OF_FIRST_OBS_LABEL)
            hour = str2int(line[18:24], "Invalid hour value in " + TIME_OF_FIRST_OBS_LABEL)
            minute = str2int(line[24:30], "Invalid minute value in " + TIME_OF_FIRST_OBS_LABEL)
            full_seconds = str2int(line[30:35], "Invalid seconds value in " + TIME_OF_FIRST_OBS_LABEL)
            # RINEX uses 7 decimals for seconds value, meaning that the lowest digit is 100 nanoseconds
            nanoseconds = str2int(line[36:43],
                                  "Invalid nanoseconds value in " + TIME_OF_FIRST_OBS_LABEL) * 100
            start_time = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{min:02d}:{sec:02d}".format(year=year,
                                                                                                  month=month,
                                                                                                  day=day,
                                                                                                  hour=hour,
                                                                                                  min=minute,
                                                                                                  sec=full_seconds)
            result.time_of_first_observation = np.datetime64(start_time) + np.timedelta64(nanoseconds, 'ns')
            result.system_time = line[48:51] if result.gnss == 'M' else result.gnss
        else:
            label = line[60:80].strip()
            if label in result.other.keys():
                result.other[label] += " | " + line[:60].strip()
            else:
                result.other[label] = line[:60].strip()
        # end of for loop
    return result
