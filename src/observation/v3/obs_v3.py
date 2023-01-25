import datetime
import io
from itertools import groupby
from typing import IO, Set

import numpy as np

import common
from observation.v3.header_v3 import Header


class ObservationV3:
    def __init__(self, header: Header):
        self.header = header
        self.epochs = {}
        self.observations = 0
        self.all_satellites: Set[str] = set()

    def __str__(self):
        return str(self.header) + "\n" + str(self.epochs)


def read_epoch_line(line: str) -> (str, bool, int):
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
    current_timestamp = datetime.datetime(year, month, day, hour, minute, int(full_seconds))

    epoch_flag = common.str2int(line[31:32], "Invalid value for epoch flag")
    block_size = common.str2int(line[32:35], "Invalid value for block size") # number of satellites in current epoch

    return current_timestamp.isoformat(), epoch_flag == 0, block_size


def read_single_observation_block(lines: [str], block_name: str, observations: ObservationV3):
    for gnss, obs_lines in groupby(lines, lambda x: x[0]):
        lines_in_group = list(obs_lines)
        sv_names = [name[:3] for name in lines_in_group]
        # self.all_satellites.update(n for n in sv_names)
        list_of_obs_types = observations.header.obs_types_for_gnss(gnss).obs_types
        amount_of_obs_types = len(list_of_obs_types)
        complete_group = "".join(lines_in_group)
        result = np.genfromtxt(io.BytesIO(complete_group.encode("ascii")),
                               delimiter=(3,) + (14, 1, 1) * amount_of_obs_types,
                               usecols=range(1, 1 + 3 * amount_of_obs_types, 3),
                               names=list_of_obs_types  # column names. i.e. obs types
                               )
        if gnss in observations.epochs.keys():
            observations.epochs[gnss][block_name] = (sv_names, result)
        else:
            observations.epochs[gnss] = {block_name: (sv_names, result)}


def read_all_observation_blocks(file: IO, header: Header) -> ObservationV3:
    """

    :param file:
    :param header:
    :return:
    """
    result = ObservationV3(header)
    for line in file:
        if line.startswith('>'):
            current_block, valid_block, block_size = read_epoch_line(line)
            print("Working with block " + current_block)
            if valid_block:
                block_lines = [next(file) for _ in range(block_size)]
                if any(block_line.startswith('>') for block_line in block_lines):
                    raise ValueError("Block {name:s} has invalid size.".format(name=current_block))
                block_lines.sort()
                read_single_observation_block(block_lines, current_block, result)

        # end of for loop

    return result
