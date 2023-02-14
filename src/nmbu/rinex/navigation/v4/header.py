#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime
from typing import IO, Dict

from nmbu.rinex.common import *


class NavigationHeaderV4:
    """
    Class that holds the result of parsing header from Navigation file in version 4.
    Contains following fields:

    - agency: str
    - created_by: str
    - creation_time: datetime
    - version: float
    - file_type: str
    - gnss: str
    - other: {str: str}
    """
    def __init__(self, version: float, file_type: str, gnss: str):
        self.agency: str = ""
        self.created_by: str = ""
        self.creation_time: datetime = None
        self.version: float = version
        self.file_type: str = file_type
        self.gnss: str = gnss
        self.other: Dict[str, str] = {}


def read_navigation_header_v4(
        file: IO,
        version: float,
        file_type: str,
        gnss: str
) -> NavigationHeaderV4:
    """
    Parses input file line by line until 'END OF HEADER' line is read.
    All header lines are extracted and parsed according to Rinex V4 specification for Navigation header

    :param file: file iterator. Supposed to start at line number 2, as the first line is read by reader.__read_first_line
    :param version: version of the file as read by reader.__read_first_line
    :param file_type: type of the file as read by reader.__read_first_line
    :param gnss: gnss of the file as read by reader.__read_first_line
    :return: NavigationHeaderV4 object filled with necessary data
    """
    result = NavigationHeaderV4(version, file_type, gnss)

    for line in file:
        if line.__contains__(END_OF_HEADER_LABEL):
            break

        if line.__contains__(PGM_RUNBY_DATE_LABEL):
            result.created_by = line[:20].strip()
            result.agency = line[20:40].strip()
            result.creation_time = datetime.strptime(line[40:60].strip(), "%Y%m%d %H%M%S %Z")
        else:
            label = line[60:80].strip()
            if label in result.other.keys():
                result.other[label] += " | " + line[:60].strip()
            else:
                result.other[label] = line[:60].strip()
        # end of for loop

    return result
