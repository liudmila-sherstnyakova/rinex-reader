import datetime
from typing import IO, Dict

from common import *


class NavigationHeaderV3:
    def __init__(self, version: float, file_type: str, gnss: str):
        self.agency: str = ""
        self.created_by: str = ""
        self.creation_time: datetime = None
        self.version: float = version
        self.file_type: str = file_type
        self.gnss: str = gnss
        self.other: Dict[str, str] = {}


def read_navigation_header_v3(
        file: IO,
        version: float,
        file_type: str,
        gnss: str
) -> NavigationHeaderV3:
    result = NavigationHeaderV3(version, file_type, gnss)

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
