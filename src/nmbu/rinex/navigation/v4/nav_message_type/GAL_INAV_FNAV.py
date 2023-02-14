import io
from datetime import datetime

import numpy as np


class GALNavRecordOrbitData:
    def __init__(self):
        # b-orbit 1
        self.IODnav: float = 0.0
        self.C_rs: float = 0.0
        self.Delta_n: float = 0.0
        self.M0: float = 0.0
        # b-orbit 2
        self.C_uc: float = 0.0
        self.e: float = 0.0
        self.C_us: float = 0.0
        self.sqrt_a: float = 0.0
        # b-orbit 3
        self.Toe: float = 0.0
        self.C_ic: float = 0.0
        self.OMEGA0: float = 0.0
        self.C_is: float = 0.0
        # b-orbit 4
        self.i0: float = 0.0
        self.C_rc: float = 0.0
        self.omega: float = 0.0
        self.OMEGA_DOT: float = 0.0
        # b-orbit 5
        self.IDOT: float = 0.0
        self.Data_sources: float = 0.0
        self.GAL_Week_no: float = 0.0
        # b-orbit 6
        self.SISA: float = 0.0
        self.SV_health: float = 0.0
        self.BGD_E5a_E1: float = 0.0
        self.BGD_E5b_E1: float = 0.0
        # b-orbit 7
        self.transmission_time: float = 0.0


class GALINAVFNAVRecord:
    gnss_symbol = 'E'
    nav_message_type = ('INAV', 'FNAV')
    block_size = 7  # amount of orbits

    epoch_line_format = np.dtype([
        ('SV', 'S8'),
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('clock_bias', np.float64), ('clock_drift', np.float64), ('clock_drift_rate', np.float64),
    ])
    delimiter = (4, 4) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv = sv
        self.timestamp = ""
        # epoch line
        self.clock_bias: float = 0.0
        self.clock_drift: float = 0.0
        self.clock_drift_rate: float = 0.0
        self.orbit_data = GALNavRecordOrbitData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=GALINAVFNAVRecord.delimiter,
                              dtype=GALINAVFNAVRecord.epoch_line_format,
                              autostrip=True
                              )
        self.timestamp = datetime(
            epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
        ).isoformat()
        self.clock_bias = epoch["clock_bias"] * 1
        self.clock_drift = epoch["clock_drift"] * 1
        self.clock_drift_rate = epoch["clock_drift_rate"] * 1

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.orbit_data.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.orbit_data.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.orbit_data.__dict__.keys():
            self.orbit_data.__dict__[p] = result[p] * 1  # convert to float
