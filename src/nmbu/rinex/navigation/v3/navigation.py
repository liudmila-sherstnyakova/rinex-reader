#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import io
from datetime import datetime
from typing import Dict, IO

import numpy as np

from nmbu.rinex.common import normalize_data_string
from nmbu.rinex.navigation.v3.nav_message_type.BDS import BDSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GAL import GALNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GLOv3_04 import GLONavRecord as GLO3_04NavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GLOv3_05 import GLONavRecord as GLO3_05NavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GPS import GPSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.IRN import IRNNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.QZS import QZSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.SBAS import SBASNavRecord


class NavigationV3:
    """
    Class that holds blocks of navigation data grouped by satellite name.
    Depending on the actual GNSS, fields may vary.
    Supported GNSS are:

    - BDS. See navigation.v3.nav_message_type.BDS.BDSNavRecord
    - GAL. See navigation.v3.nav_message_type.GAL.GALNavRecord
    - GLO. See navigation.v3.nav_message_type.GLO.GLONavRecord
    - GPS. See navigation.v3.nav_message_type.GPS.GPSNavRecord
    - IRN. See navigation.v3.nav_message_type.IRN.IRNNavRecord
    - QZS. See navigation.v3.nav_message_type.QZS.QZSNavRecord
    - SBAS. See navigation.v3.nav_message_type.SBAS.SBASNavRecord

    Examples
    --------

    >>> nav.satellites['C01']['2022-01-01T01:00:00'].clock_bias
    >>> nav.satellites['C01']['2022-01-01T01:00:00'].AODC
    """
    def __init__(self):
        self.satellites: Dict[str, Dict[str, np.void]] = {}


def __read_epoch_line(
        line: str,
        version: float
) -> (object, bool, int):
    """
    Reads epoch line for the given block.

    ValueError is raised if an unsupported GNSS is met.

    :param line: epoch line, e.g. 'C11 2022 09 29 10 00 00-3.808789188042E-04 2.210320815266E-11-3.252606517457E-19'
    :return: tuple with nav block of correct type, valid block flag and size of the given block
    """
    gnss = line[0]

    if gnss == GPSNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GPSNavRecord.delimiter,
                              dtype=GPSNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GPSNavRecord.block_size
        block = GPSNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif version == 3.04 and gnss == GLO3_04NavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GLO3_04NavRecord.delimiter,
                              dtype=GLO3_04NavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GLO3_04NavRecord.block_size
        block = GLO3_04NavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.msg_frame_time = epoch["msg_frame_time"] * 1
        block.relative_frequency_bias = epoch["relative_frequency_bias"] * 1
        should_read_block = True
    elif version == 3.05 and gnss == GLO3_05NavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GLO3_05NavRecord.delimiter,
                              dtype=GLO3_05NavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GLO3_05NavRecord.block_size
        block = GLO3_05NavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.msg_frame_time = epoch["msg_frame_time"] * 1
        block.relative_frequency_bias = epoch["relative_frequency_bias"] * 1
        should_read_block = True
    elif gnss == GALNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GALNavRecord.delimiter,
                              dtype=GALNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GALNavRecord.block_size
        block = GALNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif gnss == QZSNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=QZSNavRecord.delimiter,
                              dtype=QZSNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = QZSNavRecord.block_size
        block = QZSNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif gnss == BDSNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=BDSNavRecord.delimiter,
                              dtype=BDSNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = BDSNavRecord.block_size
        block = BDSNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif gnss == IRNNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=IRNNavRecord.delimiter,
                              dtype=IRNNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = IRNNavRecord.block_size
        block = IRNNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif gnss == SBASNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=SBASNavRecord.delimiter,
                              dtype=SBASNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = SBASNavRecord.block_size
        block = SBASNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.relative_frequency_bias = epoch["relative_frequency_bias"] * 1
        block.msg_transmission_time = epoch["msg_transmission_time"] * 1
        should_read_block = True
    else:
        raise ValueError("Unsupported GNSS: " + gnss)

    return block, should_read_block, block_size


def read_navigation_blocks_v3(
        file: IO,
        version: float,
        verbose: bool = False
) -> NavigationV3:
    """
    Parses input file and reads all navigation blocks one by one.

    ValueError is raised if any error occurs.

    :param file: file iterator. Supposed to start at 'END OF HEADER' line
    :param version: RINEX version. Used to differentiate GLONASS V3.04 from GLONASS V3.05
    :param verbose: boolean flag to control debug output to console
    :return: NavigationV3 object containing read data
    """
    result = NavigationV3()
    for line in file:
        if line[0] != ' ':
            current_block, valid_block, block_size = __read_epoch_line(line, version)
            if verbose:
                print("Working with block", current_block)
            block_lines = [normalize_data_string(next(file)) for _ in range(block_size)]
            if any(block_line[0] not in (' ', '-') for block_line in block_lines):
                raise ValueError("Block {name:s} has invalid size.".format(
                    name=current_block.sv + current_block.timestamp))
            if valid_block:
                current_block.read_lines(block_lines)
                if current_block.sv not in result.satellites:
                    result.satellites[current_block.sv] = {current_block.timestamp: current_block.orbit_data}
                else:
                    result.satellites[current_block.sv][current_block.timestamp] = current_block.orbit_data

                result.satellites[current_block.sv][current_block.timestamp].timestamp = current_block.timestamp

                if current_block.gnss_symbol in ('G', 'C', 'E'):
                    result.satellites[current_block.sv][current_block.timestamp].clock_bias = current_block.clock_bias
                    result.satellites[current_block.sv][current_block.timestamp].clock_drift = current_block.clock_drift
                    result.satellites[current_block.sv][current_block.timestamp].clock_drift_rate = current_block.clock_drift_rate
                elif current_block.gnss_symbol in ('R', 'S'):
                    result.satellites[current_block.sv][current_block.timestamp].clock_bias = current_block.clock_bias
                    result.satellites[current_block.sv][current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                    result.satellites[current_block.sv][current_block.timestamp].msg_frame_time = current_block.msg_frame_time
                # elif current_block.gnss_symbol in ('S',):
                #     result.satellites[current_block.sv][current_block.timestamp].clock_bias = current_block.clock_bias
                #     result.satellites[current_block.sv][current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                #     result.satellites[current_block.sv][current_block.timestamp].msg_transmission_time = current_block.msg_transmission_time
        else:
            raise ValueError("Navigation file seems to be invalid. Stopped reading at line\n", line)
        # end of for loop

    return result
