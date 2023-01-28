import io
from typing import Optional, List

import common
from common.rinex_data import RinexData
from observation.v3.header import *
from observation.v3.observation import read_observation_blocks_v3


def __read_first_line(line: str, verbose: bool = False) -> (float, str, str):
    """
    Reads first line from RINEX file to determine version
    :param line: first line from RINEX file
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
        *,
        start_epoch: Optional[str] = None,
        end_epoch: Optional[str] = None,
        gnss: Optional[List[str]] = None,
        obs_types: Optional[str] = None,
        verbose: bool = False
) -> RinexData:
    """
    Reads the specified RINEX file

    Correct parser is chosen based on the version and the file type,
    that are extracted from the first line.
    :param limit:
    :param rinex_file_path: path to the RINEX file
    :param verbose: boolean flag to control debug output from the script.
                    Set to True if debug output should be printed to console.
    :return: RinexData object, that contains header and data
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
        else:
            # TODO implement reading of navigation files
            raise NotImplementedError("Navigation file type is not yet supported")

    elif version in (4.0,):
        # implement reading of RINEX 4
        raise NotImplementedError("RINEX version 4.00 is not yet supported")

    else:
        raise ValueError("Unknown RINEX version. Expected 3.04|3.05|4.00, but got {v:.2f}".format(v=version))

    file.close()
    return result
