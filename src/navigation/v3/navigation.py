import io
from datetime import datetime
from typing import Dict, IO

import numpy as np

from navigation.v3.gnss.bds import BDSNavRecord
from navigation.v3.gnss.galileo import GalileoNavRecord
from navigation.v3.gnss.glonass import GLONASSNavRecord
from navigation.v3.gnss.gps import GPSNavRecord
from navigation.v3.gnss.irn import IRNNavRecord
from navigation.v3.gnss.qzss import QZSSNavRecord
from navigation.v3.gnss.sbas import SBASNavRecord


class NavigationV3:
    def __init__(self):
        self.satellites: Dict[str, Dict[str, np.void]] = {}


def __normalize_data_string(string: str) -> str:
    result = string.strip("\n")
    if len(result) < 80:
        result = result.ljust(80)
    if result.startswith("    "):
        result = result[4:]
    return result


def __read_epoch_line(
        line: str
) -> (object, bool, int):
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
    elif gnss == GLONASSNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GLONASSNavRecord.delimiter,
                              dtype=GLONASSNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GLONASSNavRecord.block_size
        block = GLONASSNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.msg_frame_time = epoch["msg_frame_time"] * 1
        block.relative_frequency_bias = epoch["relative_frequency_bias"] * 1
        should_read_block = True
    elif gnss == GalileoNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GalileoNavRecord.delimiter,
                              dtype=GalileoNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = GalileoNavRecord.block_size
        block = GalileoNavRecord(
            sv=str(np.char.decode(epoch["SV"])),
            timestamp=datetime(
                epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
            ).isoformat()
        )
        block.clock_bias = epoch["clock_bias"] * 1
        block.clock_drift = epoch["clock_drift"] * 1
        block.clock_drift_rate = epoch["clock_drift_rate"] * 1
        should_read_block = True
    elif gnss == QZSSNavRecord.gnss_symbol:
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=QZSSNavRecord.delimiter,
                              dtype=QZSSNavRecord.epoch_line_format,
                              autostrip=True
                              )
        block_size = QZSSNavRecord.block_size
        block = QZSSNavRecord(
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
        verbose: bool = False
) -> NavigationV3:
    result = NavigationV3()
    for line in file:
        if line[0] != ' ':
            current_block, valid_block, block_size = __read_epoch_line(line)
            if verbose:
                print("Working with block", current_block)
            block_lines = [__normalize_data_string(next(file)) for _ in range(block_size)]
            if any(block_line[0] not in (' ', '-') for block_line in block_lines):
                raise ValueError("Block {name:s} has invalid size.".format(
                    name=current_block.sv + current_block.timestamp))
            if valid_block:
                current_block.read_lines(block_lines)
                if current_block.sv not in result.satellites:
                    result.satellites[current_block.sv] = {current_block.timestamp: current_block.orbit_data}
                else:
                    result.satellites[current_block.sv][current_block.timestamp] = current_block.orbit_data

                if current_block.gnss_symbol in ('G', 'C', 'E'):
                    result.satellites[current_block.sv][current_block.timestamp].clock_bias = current_block.clock_bias
                    result.satellites[current_block.sv][current_block.timestamp].clock_drift = current_block.clock_drift
                    result.satellites[current_block.sv][current_block.timestamp].clock_drift_rate = current_block.clock_drift_rate
                elif current_block.gnss_symbol in ('R'):
                    result.satellites[current_block.sv][current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                    result.satellites[current_block.sv][current_block.timestamp].msg_frame_time = current_block.msg_frame_time
                elif current_block.gnss_symbol in ('S'):
                    result.satellites[current_block.sv][current_block.timestamp].relative_frequency_bias = current_block.relative_frequency_bias
                    result.satellites[current_block.sv][current_block.timestamp].msg_transmission_time = current_block.msg_transmission_time
        else:
            raise ValueError("Navigation file seems to be invalid. Stopped reading at line\n", line)
        # end of for loop

    return result
