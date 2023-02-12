import io
from datetime import datetime

import numpy as np


class EOPNavRecordData:
    def __init__(self):
        # message line 1
        self.spare1: float = 0.0
        self.Yp: float = 0.0
        self.dYpdt: float = 0.0
        self.dYpdt2: float = 0.0
        # message line 2
        self.t_tm: float = 0.0
        self.deltaUT1: float = 0.0
        self.ddeltaUT1dt: float = 0.0
        self.ddeltaUT1dt2: float = 0.0


class EOPNavRecord:
    nav_message_type = 'EOP'
    block_size = 2  # amount of orbits

    epoch_line_format = np.dtype([
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('Xp', np.float64), ('dXpdt', np.float64), ('dXpdt2', np.float64)
    ])
    delimiter = (8,) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv = sv
        self.timestamp = ""
        # epoch line
        self.xp: float = 0.0
        self.dxp_dt: float = 0.0
        self.dxp_dt2: float = 0.0
        self.message_line = EOPNavRecordData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=self.delimiter,
                              dtype=self.epoch_line_format,
                              autostrip=True
                              )
        self.timestamp = datetime(
            epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
        ).isoformat()
        self.xp = epoch["Xp"] * 1
        self.dxp_dt = epoch["dXpdt"] * 1
        self.dxp_dt2 = epoch["dXpdt2"] * 1

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.message_line.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.message_line.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.message_line.__dict__.keys():
            self.message_line.__dict__[p] = result[p] * 1  # convert to float
