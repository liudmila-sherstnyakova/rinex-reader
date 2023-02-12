import io
from datetime import datetime

import numpy as np


class STONavRecordData:
    def __init__(self):
        # message line 1
        self.t_tm: float = 0.0
        self.A0: float = 0.0
        self.A1: float = 0.0
        self.A2: float = 0.0


class STONavRecord:
    nav_message_type = 'STO'
    block_size = 1  # amount of orbits

    epoch_line_format = np.dtype([
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('time_offset', 'S19'), ('SBAS_ID', 'S19'), ('UTC_ID', 'S19'),
    ])
    delimiter = (8,) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv = sv
        self.timestamp = ""
        # epoch line
        self.time_offset: str = ""
        self.sbas_id: str = ""
        self.utc_id: str = ""
        self.message_line = STONavRecordData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=self.delimiter,
                              dtype=self.epoch_line_format,
                              autostrip=True
                              )
        self.timestamp = datetime(
            epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
        ).isoformat()
        self.time_offset = str(np.char.decode(epoch["time_offset"]))
        self.sbas_id = str(np.char.decode(epoch["SBAS_ID"]))
        self.utc_id = str(np.char.decode(epoch["UTC_ID"]))

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.message_line.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.message_line.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.message_line.__dict__.keys():
            self.message_line.__dict__[p] = result[p] * 1  # convert to float
