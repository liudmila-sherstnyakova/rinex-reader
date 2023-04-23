import io
from datetime import datetime

import numpy as np


class BDSNavRecordOrbitData:
    def __init__(self):
        # b-orbit 1
        self.A_DOT: float = 0.0
        self.Crs: float = 0.0
        self.Delta_n: float = 0.0
        self.M0: float = 0.0
        # b-orbit 2
        self.Cuc: float = 0.0
        self.e: float = 0.0
        self.Cus: float = 0.0
        self.sqrt_A: float = 0.0
        # b-orbit 3
        self.Toe: float = 0.0
        self.Cic: float = 0.0
        self.OMEGA0: float = 0.0
        self.Cis: float = 0.0
        # b-orbit 4
        self.i0: float = 0.0
        self.Crc: float = 0.0
        self.omega: float = 0.0
        self.OMEGA_DOT: float = 0.0
        # b-orbit 5
        self.IDOT: float = 0.0
        self.Delta_n_dot: float = 0.0
        self.SatType: float = 0.0
        self.t_op: float = 0.0
        # b-orbit 6
        self.SISAI_oe: float = 0.0
        self.SISAI_ocb: float = 0.0
        self.SISAI_oc1: float = 0.0
        self.SISAI_oc2: float = 0.0
        # b-orbit 7
        self.spare1: float = 0.0
        self.ISC_B2ad: float = 0.0
        self.TGD_B1Cp: float = 0.0
        self.TGD_B2ap: float = 0.0
        # b-orbit 8
        self.SISMAI: float = 0.0
        self.health: float = 0.0
        self.B2a_B1C_integrity_flag: float = 0.0
        self.IODC: float = 0.0
        # b-orbit 9
        self.t_tm: float = 0.0
        self.spare2: float = 0.0
        self.spare3: float = 0.0
        self.IODE: float = 0.0


class BDSCNAV2Record:
    gnss_symbol = 'C'
    nav_message_type = 'CNV2'
    block_size = 9  # amount of orbits

    epoch_line_format = np.dtype([
        ('SV', 'S8'),
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('clock_bias', np.float64), ('clock_drift', np.float64), ('clock_drift_rate', np.float64),
    ])
    delimiter = (4, 4) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv: str = sv
        self.timestamp: str = ""
        # epoch line
        self.clock_bias: float = 0.0
        self.clock_drift: float = 0.0
        self.clock_drift_rate: float = 0.0
        self.orbit_data = BDSNavRecordOrbitData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=BDSCNAV2Record.delimiter,
                              dtype=BDSCNAV2Record.epoch_line_format,
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

        # TODO decide what to do with TGD and set self.orbit_data.TGD here. See e.g. GAL_INAV_FNAV.py
