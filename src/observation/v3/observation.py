from datetime import datetime
from itertools import groupby
from typing import Dict, IO, List, Optional
import numpy as np
import io
import re

import common
from observation.v3.header import ObservationHeaderV3


class SingleObservationV3:
    format = np.dtype([('value', np.float64), ('ssi', np.int32), ('lli', np.int32)])

    def __init__(self, value: Optional[float], ssi: Optional[int], lli: Optional[int]):
        self.value = value
        self.lli = lli
        self.ssi = ssi


class ObservationV3:
    def __init__(self):
        # {
        #  sv: {
        #           t0: (c1c,l1c,...)
        #           t1: (c1c,l1c,...)
        #           t5: (c1c,l1c,...)
        #      }
        # }
        self.satellites: Dict[str, Dict[str, object]] = {}

    def __str__(self):
        return str(self.satellites)


def __read_epoch_line(
        line: str,
        start_epoch: Optional[datetime],
        end_epoch: Optional[datetime]
) -> (str, bool, int):
    """
    Reads epoch line for the given block
    :param line:
    :return:
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
        lines: [str],
        block_name: str,
        observations: ObservationV3,
        header: ObservationHeaderV3,
        gnss: Optional[List[str]],
        obs_types: Optional[str],
        verbose: bool = False
):
    for system, obs_lines in groupby(lines, lambda x: x[0]):

        if gnss is not None and system not in gnss:
            # skip gnss that are not in the requested limitation
            if verbose:
                print("[{block:s}] Skipped gnss {g:s} due to GNSS limitation".format(block=block_name, g=system))
            continue

        lines_in_group = list(obs_lines)
        sv_names = [name[:3] for name in lines_in_group]
        # self.all_satellites.update(n for n in sv_names)
        if obs_types is not None:
            rule = re.compile(obs_types)
            list_of_obs_types = list(filter(rule.match, header.obs_types[system]))
        else:
            list_of_obs_types = header.obs_types[system]
        if len(list_of_obs_types) == 0:
            if verbose:
                print("[{block:s}] Skipped gnss {g:s} due to OBS TYPES limitation".format(block=block_name, g=system))
            continue
        amount_of_obs_types = len(header.obs_types[system])
        complete_group = "".join(lines_in_group)
        result = np.genfromtxt(io.BytesIO(complete_group.encode("ascii")),
                               delimiter=(3,) + (14, 1, 1) * amount_of_obs_types,
                               dtype=[('SV', 'S8')] + [(name, SingleObservationV3.format) for name in header.obs_types[system]],
                               # usecols=list(range(1, 1 + 3 * amount_of_obs_types, 3)),
                               # names=header.obs_types[system]  # column names. i.e. obs types
                               )
        result = result[list_of_obs_types]  # reduce result to only the selection of obs types
        for i in range(len(sv_names)):
            if sv_names[i] not in observations.satellites.keys():
                observations.satellites[sv_names[i]] = {block_name: ""}
            observations.satellites[sv_names[i]][block_name] = result[i]

        # if system in observations.epochs.keys():
        #     observations.epochs[system][block_name] = (sv_names, result)
        # else:
        #     observations.epochs[system] = {block_name: (sv_names, result)}


def read_observation_blocks_v3(
        file: IO,
        header: ObservationHeaderV3,
        start_epoch: Optional[datetime],
        end_epoch: Optional[datetime],
        gnss: Optional[List[str]],
        obs_types: Optional[str],
        verbose: bool = False
) -> ObservationV3:
    """

    :param verbose:
    :param file:
    :param header:
    :return:
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
