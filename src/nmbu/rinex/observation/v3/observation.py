#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import io
import re
from datetime import datetime
from itertools import groupby
from typing import Dict, IO, List, Optional, Union

import numpy as np

from nmbu.rinex import common
from nmbu.rinex.observation.v3.header import ObservationHeaderV3

__single_observation_v3_format = np.dtype([('value', np.float64), ('lli', np.int32), ('ssi', np.int32)])


class ObservationV3:
    """
    Class that holds blocks of observation data grouped by satellite name.

    Examples
    --------

    >>> obs.satellites['C01']['2022-01-01T01:00:00']['C2I']['value']
    >>> obs.satellites['C01']['2022-01-01T01:00:00']['C2I']['ssi']
    >>> obs.satellites['C01']['2022-01-01T01:00:00']['C2I']['lli']
    """
    def __init__(self):
        # {
        #  sv: {
        #           t0: (c1c,l1c,...)
        #           t1: (c1c,l1c,...)
        #           t5: (c1c,l1c,...)
        #      }
        # }
        self.satellites: Dict[str, Dict[str, np.void]] = {}

    def __str__(self):
        return str(self.satellites)


def __read_epoch_line(
        line: str,
        start_epoch: Optional[datetime],
        end_epoch: Optional[datetime]
) -> (str, bool, int):
    """
    Methods that reads start line for each observation record block.
    Epoch time filter is applied to decide if current block should be read.

    :param line: str.
        Required. Epoch start line.
    :param start_epoch: datetime.
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        If used together with end_epoch, all blocks within the given timeframe will be read.
        If used alone, the result will contain at most one block - the one that matches provided timestamp exactly.
    :param end_epoch: datetime.
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        When used, must be a date after the start_epoch date.
    :return: Tuple(str, bool, int).
        Returns three params:
        * block name as ISO8601 formatted timestamp
        * True/False if current block is valid or should be skipped due to filter
        * block size - amount of lines with observations in current block
    """
    year = common.str2int(line[2:6], "Invalid year value in epoch line")
    month = common.str2int(line[7:9], "Invalid month value in epoch line")
    day = common.str2int(line[10:12], "Invalid day value in epoch line")
    hour = common.str2int(line[13:15], "Invalid hour value in epoch line")
    minute = common.str2int(line[16:18], "Invalid minute value in epoch line")
    full_seconds = common.str2float(line[19:29], "Invalid seconds value in epoch line")
    current_timestamp = datetime(year, month, day, hour, minute, int(full_seconds))

    epoch_flag = common.str2int(line[31:32], "Invalid value for epoch flag")
    block_size = common.str2int(line[32:35], "Invalid value for block size")  # number of satellites in current epoch

    should_read_block = True

    if start_epoch is not None:
        if end_epoch is None:
            should_read_block = current_timestamp == start_epoch
        else:
            should_read_block = start_epoch <= current_timestamp <= end_epoch

    return current_timestamp.isoformat(), epoch_flag == 0 and should_read_block, block_size


def __read_single_observation_block(
        lines: List[str],
        block_name: str,
        observations: ObservationV3,
        header: ObservationHeaderV3,
        gnss: Optional[List[str]],
        obs_types: Union[str, List[str], None],
        verbose: bool = False
) -> None:
    """
    Reads all lines that constitute a complete observation record block.

    :param lines: List[str].
        Required. List of lines that make up the block.
        Method will run a groupby operation on the list, so the list must be sorted alphabetically.
    :param block_name: str.
        Required. Name of the current block. Typically a timestamp string in ISO8601 format.
    :param observations: ObservationV3.
        Required. Object that will be updated with observations from the given block.
    :param header: ObservationHeaderV3.
        Required. Header object with data read from the RINEX header
    :param gnss: List[str].
        Optional. GNSS filter. Specifies GNSS types (e.g. 'G' or 'E') that will be included into the result.
        All other GNSS will be ignored.
    :param obs_types: str or List[str].
        Optional. Observation types filter.
        If a single string is provided, it is treated as regex and used to filter obs types for all satellites.
        If a list of strings is provided, then only that list is used to filter obs types.
        If a GNSS does not have any obs types from that list, then that GNSS is not included in the result.
    :param verbose: bool.
        Optional. Flag to control debug output from the script.
        Set to True if debug output should be printed to console.
    :return: Nothing
    """
    for system, obs_lines in groupby(lines, lambda x: x[0]):

        if gnss is not None and system not in gnss:
            # skip nav_message_type that are not in the requested limitation
            if verbose:
                print("[{block:s}] Skipped nav_message_type {g:s} due to GNSS limitation".format(block=block_name, g=system))
            continue

        lines_in_group = list(obs_lines)
        sv_names = [name[:3] for name in lines_in_group]
        if obs_types is not None:
            if isinstance(obs_types, str):
                rule = re.compile(obs_types)
                list_of_obs_types = list(filter(rule.match, header.obs_types[system]))
            else:
                list_of_obs_types = list(set(obs_types) & set(header.obs_types[system]))
        else:
            list_of_obs_types = header.obs_types[system]
        if len(list_of_obs_types) == 0:
            if verbose:
                print("[{block:s}] Skipped nav_message_type {g:s} due to OBS TYPES limitation".format(block=block_name, g=system))
            continue
        amount_of_obs_types = len(header.obs_types[system])
        complete_group = "".join(lines_in_group)
        result = np.genfromtxt(io.BytesIO(complete_group.encode("ascii")),
                               delimiter=(3,) + (14, 1, 1) * amount_of_obs_types,
                               dtype=[('SV', 'S8')] + [(name, __single_observation_v3_format) for name in header.obs_types[system]]
                               )
        if verbose:
            print("For GNSS '{gnss:s}' only following obs types are included: {types:s}".format(
                gnss=system,
                types=str(list_of_obs_types)))
        result = result[list_of_obs_types]  # reduce result to only the selection of obs types
        for i in range(len(sv_names)):
            if sv_names[i] not in observations.satellites.keys():
                observations.satellites[sv_names[i]] = {block_name: np.nan}
            observations.satellites[sv_names[i]][block_name] = result[i]


def read_observation_blocks_v3(
        file: IO,
        header: ObservationHeaderV3,
        start_epoch: Optional[datetime],
        end_epoch: Optional[datetime],
        gnss: Optional[List[str]],
        obs_types: Union[str, List[str], None],
        verbose: bool = False
) -> ObservationV3:
    """
    Iterates through the Rinex file to read all observation records.
    Skips all blocks that should not be included, based on epoch flag and time filter

    :param file: IO.
        File iterator that reads file line by line.
        Position of this iterator is expected to be on the 'END OF HEADER' line
    :param header: ObservationHeaderV3.
        observation.v3.header.ObservationHeaderV3 object that is filled with data from header
    :param start_epoch: datetime.
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        If used together with end_epoch, all blocks within the given timeframe will be read.
        If used alone, the result will contain at most one block - the one that matches provided timestamp exactly.
    :param end_epoch: datetime.
        Optional. Epoch time filter. Specifies start of the period that should be included in the result.
        When used, must be a date after the start_epoch date.
    :param gnss: List[str].
        Optional. GNSS filter. Specifies GNSS types (e.g. 'G' or 'E') that will be included into the result.
        All other GNSS will be ignored.
    :param obs_types: str or List[str].
        Optional. Observation types filter.
        If a single string is provided, it is treated as regex and used to filter obs types for all satellites.
        If a list of strings is provided, then only that list is used to filter obs types.
        If a GNSS does not have any obs types from that list, then that GNSS is not included in the result.
    :param verbose: bool.
        Optional. Flag to control debug output from the script.
        Set to True if debug output should be printed to console.
    :return: ObservationV3.
        Holder class that contains observation record data. See observation.v3.observation.ObservationV3
    """
    result = ObservationV3()
    for line in file:
        if line.startswith('>'):
            current_block, valid_block, block_size = __read_epoch_line(line, start_epoch, end_epoch)
            if verbose:
                print("Working with block " + current_block)
            if valid_block:
                block_lines = [next(file) for _ in range(block_size)]
                if any(block_line.startswith('>') for block_line in block_lines):
                    raise ValueError("Block {name:s} has invalid size.".format(name=current_block))
                block_lines.sort()
                __read_single_observation_block(block_lines, current_block, result, header, gnss, obs_types, verbose)
            else:
                # skip N lines of block
                for _ in range(block_size):
                    next(file)

        # end of for loop

    return result
