import io
from datetime import datetime

import numpy as np


class IONBDGIMNavRecordData:
    def __init__(self):
        # message line 1
        self.Alpha4: float = 0.0
        self.Alpha5: float = 0.0
        self.Alpha6: float = 0.0
        self.Alpha7: float = 0.0
        # message line 2
        self.Alpha8: float = 0.0
        self.Alpha9: float = 0.0


class IONBDGIMNavRecord:
    nav_message_type = 'ION'
    block_size = 2  # amount of message line

    epoch_line_format = np.dtype([
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('Alpha1', np.float64), ('Alpha2', np.float64), ('Alpha3', np.float64)
    ])
    delimiter = (8,) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str):
        self.sv = sv
        self.timestamp = ""
        # epoch line
        self.Alpha1: float = 0.0
        self.Alpha2: float = 0.0
        self.Alpha3: float = 0.0
        self.message_line = IONBDGIMNavRecordData()

    def read_epoch_line(self, line: str):
        epoch = np.genfromtxt(io.BytesIO(line.encode("ascii")),
                              delimiter=self.delimiter,
                              dtype=self.epoch_line_format,
                              autostrip=True
                              )
        self.timestamp = datetime(
            epoch["year"], epoch["month"], epoch["day"], epoch["hour"], epoch["min"], epoch["sec"]
        ).isoformat()
        self.Alpha1 = epoch["Alpha1"] * 1
        self.Alpha2 = epoch["Alpha2"] * 1
        self.Alpha3 = epoch["Alpha3"] * 1

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.message_line.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.message_line.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.message_line.__dict__.keys():
            self.message_line.__dict__[p] = result[p] * 1  # convert to float
