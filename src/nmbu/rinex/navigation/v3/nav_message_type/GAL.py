import io

import numpy as np


class GALNavRecordOrbitData:
    def __init__(self):
        # b-orbit 1
        self.IODnav: float = 0.0
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
        self.Data_sources: float = 0.0
        self.GAL_Week_no: float = 0.0
        self.spare1: float = 0.0
        # b-orbit 6
        self.SISA: float = 0.0
        self.SV_health: float = 0.0
        self.BGD_E5a_E1: float = 0.0
        self.BGD_E5b_E1: float = 0.0
        # b-orbit 7
        self.t_tm: float = 0.0
        self.spare2: float = 0.0
        self.spare3: float = 0.0
        self.spare4: float = 0.0


class GALNavRecord:
    gnss_symbol = 'E'

    block_size = 7  # amount of orbits

    epoch_line_format = np.dtype([
        ('SV', 'S8'),
        ('year', np.int32), ('month', np.int32), ('day', np.int32),
        ('hour', np.int32), ('min', np.int32), ('sec', np.int32),
        ('clock_bias', np.float64), ('clock_drift', np.float64), ('clock_drift_rate', np.float64),
    ])
    delimiter = (4, 4) + (3,) * 5 + (19,) * 3

    ion_corr_line_format = np.dtype([
        ('ai0', np.float64), ('ai1', np.float64), ('ai2', np.float64), ('ai3', np.float64)
    ])

    def __init__(self, sv: str, timestamp: str):
        self.sv = sv
        self.timestamp = timestamp
        # epoch line
        self.clock_bias: float = 0.0
        self.clock_drift: float = 0.0
        self.clock_drift_rate: float = 0.0
        self.orbit_data = GALNavRecordOrbitData()

    def read_lines(self, lines: [str]):
        whole_block = "".join(lines)
        result = np.genfromtxt(io.BytesIO(whole_block.encode("ascii")),
                               delimiter=(19,) * len(self.orbit_data.__dict__),
                               dtype=np.dtype([(param, np.float64) for param in self.orbit_data.__dict__.keys()]),
                               autostrip=True
                               )
        for p in self.orbit_data.__dict__.keys():
            self.orbit_data.__dict__[p] = result[p] * 1  # convert to float

        self.orbit_data.TGD = self.__get_correct_TGD_value__()

    def __get_correct_TGD_value__(self):
        ds_flag = int(self.orbit_data.Data_sources)
        if ds_flag & 0b00000001:  # bit 0 set
            return self.orbit_data.BGD_E5b_E1
        elif ds_flag & 0b00000010:  # bit 1 set:
            return self.orbit_data.BGD_E5a_E1
        elif ds_flag & 0b00000100:  # bit 2 set:
            return self.orbit_data.BGD_E5b_E1
        else:
            raise ValueError("Unable to determine TGD value based on Data_sources flag: {0}".format(
                self.orbit_data.Data_sources))
