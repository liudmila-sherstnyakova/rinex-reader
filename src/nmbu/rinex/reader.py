#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import io
from typing import Optional, List, Union

from nmbu.rinex import common
from nmbu.rinex.common.rinex_data import RinexData
from nmbu.rinex.navigation.v3.header import read_navigation_header_v3
from nmbu.rinex.navigation.v3.navigation import read_navigation_blocks_v3
from nmbu.rinex.navigation.v4.header import read_navigation_header_v4
from nmbu.rinex.navigation.v4.navigation import read_navigation_blocks_v4
from nmbu.rinex.observation.v3.header import *
from nmbu.rinex.observation.v3.observation import read_observation_blocks_v3
from nmbu.rinex.observation.v4.header import *
from nmbu.rinex.observation.v4.observation import read_observation_blocks_v4


def __read_first_line(line: str, verbose: bool = False) -> (float, str, str):
    """
    Reads first line from the RINEX file to determine the version, file type and GNSS type.

    Expects line to be of format:

    >>> 3.05           OBSERVATION DATA    M                   RINEX VERSION / TYPE

    This method will raise an exception if the given line contains invalid data.

    :param line: str.
        Line that contains first line of RINEX format (see spec)
    :param verbose: bool.
        Flag to control debug output from the script.
        Set to True if debug output should be printed to console.
    :return: (float, str, str)
        Tuple of (RINEX version as float, file type as str, GNSS as str)
    """
    if verbose:
        print("Reading first header line to determine RINEX version and file type...")

    assert line[60:80] == RINEX_VERSION_TYPE_LABEL, \
        "First line is expected to have label '%s', which was not found" % RINEX_VERSION_TYPE_LABEL

    version = common.str2float(line[0:9], "Invalid version value in " + RINEX_VERSION_TYPE_LABEL)

    file_type = line[20]  # Obs / Nav
    assert file_type in ['O', 'N'], "Unknown file type. Expected 'O' or 'N', but got '%s'" % file_type

    gnss = line[40]  # M or single GNSS
    assert gnss in supported_gnss, "Unknown GNSS: '%s'" % gnss

    return version, file_type, gnss


def read_rinex_file(
        rinex_file_path: str,
        *,  # all params after this point must be specified with name
        start_epoch: Optional[str] = None, # 2022-01-01T00:00:00
        end_epoch: Optional[str] = None, # 2022-01-01T00:00:00
        gnss: Optional[List[str]] = None, # ['G','E',...]
        obs_types: Union[str, List[str], None] = None, # "L1L" / ".1X" / "C.." | ["C1X", "D2Y"]
        verbose: bool = False
) -> RinexData:
    """
    Reads the specified RINEX file

    Correct parser is chosen based on the version and the file type,
    that are extracted from the first line.

    Examples
    --------
    >>> from nmbu.rinex import reader

    Simple file reading with no filtering

    >>> result = reader.read_rinex_file('path/to/rinex/file')
    >>> result
    Type: O (ver. 3.05). Contains 7 satellites

    Filtering using GNSS list

    >>> result = reader.read_rinex_file(rinex_file_path='path/to/rinex/file', gnss=['R','C'])
    >>> result
    Type: O (ver. 3.05). Contains 7 satellites

    Filtering using obs types list

    >>> result = reader.read_rinex_file(rinex_file_path='path/to/rinex/file', obs_types=['C1C','L2I'])
    >>> result
    Type: O (ver. 3.05). Contains 7 satellites

    Filtering using obs types regex
    Use '.' as wildcard for any part of the obs type acronym.
    Use '[]' as a list of accepted symbols.
    For example to select all obs types that have type C, use 'C..'
    To select all obs types with type L and band 1, use 'L1.'
    To select all obs types with types L or C and band 2, use '[C, L]2.'

    >>> result = reader.read_rinex_file(rinex_file_path='path/to/rinex/file', obs_types='C1.')
    >>> result
    Type: O (ver. 3.05). Contains 7 satellites

    Filtering using time period

    To include a single block

    >>> result = reader.read_rinex_file(rinex_file_path='path/to/rinex/file',
    ... start_epoch="2022-09-29T11:00:00")

    To include all blocks between dates

    >>> result = reader.read_rinex_file(rinex_file_path='path/to/rinex/file',
    ... start_epoch="2022-09-29T11:00:00", end_epoch="2022-09-29T11:00:40")

    Parsing the result object
    -------------------------

    To obtain single observation value/lli/ssi

    >>> result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["value"]
    >>> result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["lli"]
    >>> result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["ssi"]

    To obtain observation for the single obs type (value, lli, ssi)

    >>> result.data.satellites["R04"]["2022-09-29T11:00:30"]["C1C"]
    R04 - C1C:  (20279832.26, -1, -1)

    To obtain all channels for the given satellite

    >>> result.data.satellites["R04"]["2022-09-29T11:00:30"]
    ((20279832.26, -1, -1), (1.08597601e+08, -1, 8), (2741.776, -1, -1), (20279835.24, -1, -1),
    ... (84464829.352, -1, 8), (2132.492, -1, -1))

    To obtain only values for all channels for the given satellite

    >>> list(map(lambda x: x["value"], result.data.satellites["R04"]["2022-09-29T11:00:00"])))
    [20279832.26, 108597600.752, 2741.776, 20279835.24, 84464829.352, 2132.492]

    To filter only SVs for the given GNSS for the given timestamp, use list comprehension

    >>> {sv: bl for sv, bl in result.data.satellites.items() if "2022-09-30T04:59:40" in bl.keys() and sv.startswith('E')}
    {'C01':{'2022-09-30T04:59:40': ((27884261.6, -1, -1), (1.46532775e+08, -1, 5), ...}}

    :param rinex_file_path: str.
        Required. Path to the RINEX file
    :param start_epoch: str
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        If specified, must be a datetime string in ISO8601 format, e.g. '2022-01-01T00:00:00'.
        If used together with end_epoch, all blocks within the given timeframe will be read.
        If used alone, the result will contain at most one block - the one that matches provided timestamp exactly.
    :param end_epoch: str
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        If specified, must be a datetime string in ISO8601 format, e.g. '2022-01-01T00:00:00'.
        When used, must be a date after the start_epoch date.
    :param gnss: list of str
        Optional. GNSS filter. Specifies GNSS types (e.g. 'G' or 'E') that will be included into the result.
        All other GNSS will be ignored.
    :param obs_types: str, list of str
        Optional. Observation types filter.
        If a single string is provided, it is treated as regex and used to filter obs types for all satellites.
        If a list of strings is provided, then only that list is used to filter obs types.
        If a GNSS does not have any obs types from that list, then that GNSS is not included in the result.
    :param verbose: bool.
        Optional. Flag to control debug output from the script.
        Set to True if debug output should be printed to console.
    :return: RinexData.
        Holder class that contains header and data. See common.rinex_data.RinexData
    """
    file = io.open(file=rinex_file_path, mode='r')
    version, file_type, system = __read_first_line(file.readline(), verbose)

    if file.closed:
        raise IOError("File %s is already closed" % rinex_file_path)

    if start_epoch is not None:
        start_epoch = str2date(start_epoch)
    if end_epoch is not None:
        end_epoch = str2date(end_epoch)
        if start_epoch is None:
            raise ValueError("Time period limitation with open start and closed end is not supported.")
    if (start_epoch is None and end_epoch is not None) or \
            (start_epoch is not None and end_epoch is not None and start_epoch > end_epoch):
        raise ValueError("Invalid time period: start should be earlier than end.")

    if version in (3.04, 3.05):
        if file_type == "O":
            header = read_observation_header_v3(file, version, file_type, system)
            observations = read_observation_blocks_v3(file, header, start_epoch, end_epoch, gnss, obs_types, verbose)
            result = RinexData(header, observations)
        elif file_type == "N":
            header = read_navigation_header_v3(file, version, file_type, system)
            nav_data = read_navigation_blocks_v3(file, version, verbose)
            result = RinexData(header, nav_data)

    elif version in (4.0,):
        if file_type == "O":
            header = read_observation_header_v4(file, version, file_type, system)
            observations = read_observation_blocks_v4(file, header, start_epoch, end_epoch, gnss, obs_types, verbose)
            result = RinexData(header, observations)
        elif file_type == "N":
            header = read_navigation_header_v4(file, version, file_type, system)
            nav_data = read_navigation_blocks_v4(file, verbose)
            result = RinexData(header, nav_data)

    else:
        raise ValueError("Unknown RINEX version. Expected 3.04|3.05|4.00, but got {v:.2f}".format(v=version))

    file.close()
    return result
