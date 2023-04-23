#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Dict, IO

import numpy as np

from nmbu.rinex.common import normalize_data_string
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV1 import BDSCNAV1Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV2 import BDSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_CNAV3 import BDSCNAV3Record
from nmbu.rinex.navigation.v4.nav_message_type.BDS_D1_D2 import BDSD1D2Record
from nmbu.rinex.navigation.v4.nav_message_type.EOP import EOPNavRecord
from nmbu.rinex.navigation.v4.nav_message_type.GAL_INAV_FNAV import GALINAVFNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.GLO_FDMA import GLOFDMARecord
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV import GPSCNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.GPS_CNAV2 import GPSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.GPS_LNAV import GPSLNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.ION_Klobuchar import IONKlobNavRecord
from nmbu.rinex.navigation.v4.nav_message_type.IRN_LNAV import IRNLNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.QZS_CNAV import QZSCNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.QZS_CNAV2 import QZSCNAV2Record
from nmbu.rinex.navigation.v4.nav_message_type.QZS_LNAV import QZSLNAVRecord
from nmbu.rinex.navigation.v4.nav_message_type.SBAS import SBASNavRecord
from nmbu.rinex.navigation.v4.nav_message_type.STO import STONavRecord


class NavigationV4:
    """
    Class that holds blocks of navigation data grouped by satellite name.
    Depending on the actual GNSS, fields may vary.
    Supported GNSS are:

    - BDS_CNAV1. See navigation.v4.nav_message_type.BDS_CNAV1.BDSCNAV1Record
    - BDS_CNAV2. See navigation.v4.nav_message_type.BDS_CNAV2.BDSCNAV2Record
    - BDS_CNAV3. See navigation.v4.nav_message_type.BDS_CNAV3.BDSCNAV3Record
    - BDS_D1_D2. See navigation.v4.nav_message_type.BDS_D1_D2.BDSD1D2Record
    - GAL_INAV_FNAV. See navigation.v4.nav_message_type.GAL_INAV_FNAV.GALINAVFNAVRecord
    - GLO_FDMA. See navigation.v4.nav_message_type.GLO_FDMA.GLOFDMARecord
    - GPS_CNAV. See navigation.v4.nav_message_type.GPS_CNAV.GPSCNAVRecord
    - GPS_CNAV2. See navigation.v4.nav_message_type.GPS_CNAV2.GPSCNAV2Record
    - GPS_LNAV. See navigation.v4.nav_message_type.GPS_LNAV.GPSLNAVRecord
    - IRN_LNAV. See navigation.v4.nav_message_type.IRN_LNAV.IRNLNAVRecord
    - QZS_CNAV. See navigation.v4.nav_message_type.QZS_CNAV.QZSCNAVRecord
    - QZS_CNAV2. See navigation.v4.nav_message_type.QZS_CNAV2.QZSCNAV2Record
    - QZS_LNAV. See navigation.v4.nav_message_type.QZS_LNAV.QZSLNAVRecord
    - SBAS. See navigation.v4.nav_message_type.SBAS.SBASNavRecord

    Supported corrections are:

    - STO. See nmbu.rinex.navigation.v4.nav_message_type.STO.STONavRecord
    - EOP. See nmbu.rinex.navigation.v4.nav_message_type.EOP.EOPNavRecord
    - ION_KLOBUCHAR. See nmbu.rinex.navigation.v4.nav_message_type.ION_Klobuchar.IONKlobNavRecord


    Examples
    --------

    >>> nav.satellites['C01']['2022-01-01T01:00:00'].clock_bias
    >>> nav.satellites['C01']['2022-01-01T01:00:00'].AODC
    >>> nav.corrections['STO']['C01']['2022-01-01T01:00:00'].A0

    """
    def __init__(self):
        self.satellites: Dict[str, Dict[str, np.void]] = {}
        self.corrections: Dict[str, Dict[str, Dict[str, np.void]]] = {
            STONavRecord.nav_message_type: {},
            IONKlobNavRecord.nav_message_type: {},
            EOPNavRecord.nav_message_type: {},
        }


def __read_start_line(line: str) -> (object, bool, int):
    """
    Reads start line of a navigation block to decide block type and size

    :param line: string in format '> EPH C11 D1'
    :return: tuple with nav block of correct type, valid block flag and size of the given block
    """
    # > EPH C11 D1
    record_type = line[2:5]
    gnss = line[6]
    sv = line[6:9].strip()
    nav_message_type = line[10:14].strip()

    if record_type == "EPH":
        if gnss == 'G':
            if nav_message_type == GPSLNAVRecord.nav_message_type:
                current_block = GPSLNAVRecord(sv)
                should_read_block = True
                block_size = GPSLNAVRecord.block_size
            elif nav_message_type == GPSCNAVRecord.nav_message_type:
                current_block = GPSCNAVRecord(sv)
                should_read_block = True
                block_size = GPSCNAVRecord.block_size
            elif nav_message_type == GPSCNAV2Record.nav_message_type:
                current_block = GPSCNAV2Record(sv)
                should_read_block = True
                block_size = GPSCNAV2Record.block_size
            else:
                raise ValueError()

        elif gnss == 'E':
            if nav_message_type in GALINAVFNAVRecord.nav_message_type:
                current_block = GALINAVFNAVRecord(sv)
                should_read_block = True
                block_size = GALINAVFNAVRecord.block_size
            else:
                raise ValueError()

        elif gnss == 'R':
            if nav_message_type == GLOFDMARecord.nav_message_type:
                current_block = GLOFDMARecord(sv)
                should_read_block = True
                block_size = GLOFDMARecord.block_size
            else:
                raise ValueError()

        elif gnss == "J":
            if nav_message_type == QZSCNAVRecord.nav_message_type:
                current_block = QZSCNAVRecord(sv)
                should_read_block = True
                block_size = QZSCNAVRecord.block_size
            elif nav_message_type == QZSCNAV2Record.nav_message_type:
                current_block = QZSCNAV2Record(sv)
                should_read_block = True
                block_size = QZSCNAV2Record.block_size
            elif nav_message_type == QZSLNAVRecord.nav_message_type:
                current_block = QZSLNAVRecord(sv)
                should_read_block = True
                block_size = QZSLNAVRecord.block_size
            else:
                raise ValueError()

        elif gnss == "C":
            if nav_message_type == BDSCNAV1Record.nav_message_type:
                current_block = BDSCNAV1Record(sv)
                should_read_block = True
                block_size = BDSCNAV1Record.block_size
            elif nav_message_type == BDSCNAV2Record.nav_message_type:
                current_block = BDSCNAV2Record(sv)
                should_read_block = True
                block_size = BDSCNAV2Record.block_size
            elif nav_message_type == BDSCNAV3Record.nav_message_type:
                current_block = BDSCNAV3Record(sv)
                should_read_block = True
                block_size = BDSCNAV3Record.block_size
            elif nav_message_type in BDSD1D2Record.nav_message_type:
                current_block = BDSD1D2Record(sv)
                should_read_block = True
                block_size = BDSD1D2Record.block_size
            else:
                raise ValueError()

        elif gnss == "S":
            if nav_message_type == SBASNavRecord.nav_message_type:
                current_block = SBASNavRecord(sv)
                should_read_block = True
                block_size = SBASNavRecord.block_size
            else:
                raise ValueError()

        elif gnss == "I":
            if nav_message_type == IRNLNAVRecord.nav_message_type:
                current_block = IRNLNAVRecord(sv)
                should_read_block = True
                block_size = IRNLNAVRecord.block_size
            else:
                raise ValueError()

        else:
            raise ValueError()

    elif record_type == "STO":
        current_block = STONavRecord(sv)
        should_read_block = True
        block_size = STONavRecord.block_size
    elif record_type == "EOP":
        current_block = EOPNavRecord(sv)
        should_read_block = True
        block_size = EOPNavRecord.block_size
    elif record_type == "ION":
        # FIXME decide how to differentiate between different types of ION corrections
        current_block = IONKlobNavRecord(sv)
        should_read_block = True
        block_size = IONKlobNavRecord.block_size

    else:
        raise ValueError("Unknown record type {r:s}".format(r=record_type))

    return current_block, should_read_block, block_size


def read_navigation_blocks_v4(
        file: IO,
        verbose: bool = False
) -> NavigationV4:
    """
        Parses input file and reads all navigation blocks one by one.

        ValueError is raised if any error occurs.

        :param file: file iterator. Supposed to start at 'END OF HEADER' line
        :param verbose: boolean flag to control debug output to console
        :return: NavigationV4 object containing read data
        """
    result = NavigationV4()
    for line in file:
        if line[0] == '>':
            current_block, valid_block, block_size = __read_start_line(line)
            if verbose:
                print("Working with block", current_block)
            current_block.read_epoch_line(next(file))
            block_lines = [normalize_data_string(next(file)) for _ in range(block_size)]
            if valid_block:
                current_block.read_lines(block_lines)

                if current_block.nav_message_type not in ('STO', 'EOP', 'ION'):
                    if current_block.sv not in result.satellites:
                        result.satellites[current_block.sv] = {current_block.timestamp: current_block.orbit_data}
                    else:
                        result.satellites[current_block.sv][current_block.timestamp] = current_block.orbit_data

                    result.satellites[current_block.sv][current_block.timestamp].timestamp = current_block.timestamp

                    if current_block.gnss_symbol in ('G', 'C', 'E', 'J', 'I'):
                        result.satellites[current_block.sv][
                            current_block.timestamp].clock_bias = current_block.clock_bias
                        result.satellites[current_block.sv][
                            current_block.timestamp].clock_drift = current_block.clock_drift
                        result.satellites[current_block.sv][
                            current_block.timestamp].clock_drift_rate = current_block.clock_drift_rate
                    elif current_block.gnss_symbol == 'R':
                        result.satellites[current_block.sv][
                            current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                        result.satellites[current_block.sv][
                            current_block.timestamp].msg_frame_time = current_block.msg_frame_time
                    elif current_block.gnss_symbol == 'S':
                        result.satellites[current_block.sv][
                            current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                        result.satellites[current_block.sv][
                            current_block.timestamp].msg_transmission_time = current_block.msg_transmission_time
                else:
                    # STO/ION/EOP
                    if current_block.sv not in result.corrections[current_block.nav_message_type]:
                        result.corrections[current_block.nav_message_type][current_block.sv] = \
                            {current_block.timestamp: current_block.message_line}
                    else:
                        result.corrections[current_block.nav_message_type][
                            current_block.sv][current_block.timestamp] = current_block.message_line

                    result.corrections[current_block.nav_message_type][
                        current_block.sv][current_block.timestamp].timestamp = current_block.timestamp

                    if current_block.nav_message_type == 'STO':
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].time_offset = current_block.time_offset
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].sbas_id = current_block.sbas_id
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].utc_id = current_block.utc_id
                    elif current_block.nav_message_type == 'ION':
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].Alpha0 = current_block.Alpha0
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].Alpha1 = current_block.Alpha1
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].Alpha2 = current_block.Alpha2
                    else:  # EOP
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].xp = current_block.xp
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].dxp_dt = current_block.dxp_dt
                        result.corrections[current_block.nav_message_type][current_block.sv][
                            current_block.timestamp].dxp_dt2 = current_block.dxp_dt2

        else:
            raise ValueError("Navigation file seems to be invalid. Stopped reading at line\n", line)
        # end of for loop

    return result
