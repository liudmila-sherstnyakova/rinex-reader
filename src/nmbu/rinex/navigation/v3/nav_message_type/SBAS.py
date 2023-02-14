import io

import numpy as np


class SBASNavRecordOrbitData:
    def __init__(self):
        # b-orbit 1
        self.SV_pos_X: float = 0.0
        self.velocity_X: float = 0.0
        self.acceleration_X: float = 0.0
        self.health: float = 0.0
        # b-orbit 2
        self.SV_pos_Y: float = 0.0
        self.velocity_Y: float = 0.0
        self.acceleration_Y: float = 0.0
        self.accuracy_code: float = 0.0
        # b-orbit 3
        self.SV_pos_Z: float = 0.0
        self.velocity_Z: float = 0.0
        self.acceleration_Z: float = 0.0
        self.IODN: float = 0.0


class SBASNavRecord:
    gnss_symbol = 'S'

    block_size = 3  # amount of orbits

    epoch_line_format = np.dtype([
        ('SV', 'S8'),
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('clock_bias', np.float64), ('relative_frequency_bias', np.float64), ('msg_transmission_time', np.float64),
    ])
    delimiter = (4, 4) + (3,) * 5 + (19,) * 3

    def __init__(self, sv: str, timestamp: str):
        self.sv = sv
        self.timestamp = timestamp
        # epoch line
        self.clock_bias: float = 0.0
        self.relative_frequency_bias: float = 0.0
        self.msg_transmission_time: float = 0.0
        self.orbit_data = SBASNavRecordOrbitData()

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.orbit_data.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.orbit_data.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.orbit_data.__dict__.keys():
            self.orbit_data.__dict__[p] = result[p] * 1  # convert to float
