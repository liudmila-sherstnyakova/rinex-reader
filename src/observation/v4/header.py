RINEX_VERSION_TYPE_LABEL = "RINEX VERSION / TYPE"
MARKER_NAME_LABEL = "MARKER NAME"
ANTENNA_NO_TYPE_LABEL = "ANT # / TYPE"
ANTENNA_DELTA_HEN_LABEL = "ANTENNA: DELTA H/E/N"
APPROXIMATE_POSITION_LABEL = "APPROX POSITION XYZ"
SYS_NO_OBS_TYPES_LABEL = "SYS / # / OBS TYPES"
TIME_OF_FIRST_OBS_LABEL = "TIME OF FIRST OBS"
END_OF_HEADER_LABEL = "END OF HEADER"


class ObservationHeaderV4:
    def __init__(self, version: float, file_type: str, gnss: str):
        self.version = version
        self.file_type = file_type
        self.gnss = gnss
