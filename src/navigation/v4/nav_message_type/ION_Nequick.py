import io
from datetime import datetime

import numpy as np


class IONNeqNavRecordData:
    def __init__(self):
        # message line 1
        self.dist_flag: float = 0.0

class IONNeqNavRecord:
    nav_message_type = 'ION'
    block_size = 1  # amount of message line

    epoch_line_format = np.dtype([
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('ai0', np.float64), ('ai1', np.float64), ('ai2', np.float64)
    ])
    delimiter = (8,) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv = sv
        self.timestamp = ""
        # epoch line
        self.ai0: float = 0.0
        self.ai1: float = 0.0
        self.ai2: float = 0.0
        self.message_line = IONNeqNavRecordData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=self.delimiter,
                              dtype=self.epoch_line_format,
                              autostrip=True
                              )
        self.timestamp = datetime(
            epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
        ).isoformat()
        self.ai0 = epoch["ai0"] * 1
        self.ai1 = epoch["ai1"] * 1
        self.ai2 = epoch["ai2"] * 1

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.message_line.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.message_line.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.message_line.__dict__.keys():
            self.message_line.__dict__[p] = result[p] * 1  # convert to float
