from typing import Union

from observation.v3.header import ObservationHeaderV3
from observation.v3.observation import ObservationV3
from observation.v4.header import ObservationHeaderV4


class RinexData:
    def __init__(self,
                 header: Union[ObservationHeaderV3, ObservationHeaderV4],
                 data: ObservationV3):
        self.header = header
        self.data = data

    def __str__(self):
        return "Type: {t:s} (ver. {v:.2f}). Contains {s_no:d} satellites".format(
            t=self.header.file_type,
            v=self.header.version,
            s_no=len(self.data.satellites)
        )