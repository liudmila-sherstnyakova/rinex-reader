from datetime import datetime

RINEX_VERSION_TYPE_LABEL = "RINEX VERSION / TYPE"
MARKER_NAME_LABEL = "MARKER NAME"
ANTENNA_NO_TYPE_LABEL = "ANT # / TYPE"
ANTENNA_DELTA_HEN_LABEL = "ANTENNA: DELTA H/E/N"
APPROXIMATE_POSITION_LABEL = "APPROX POSITION XYZ"
SYS_NO_OBS_TYPES_LABEL = "SYS / # / OBS TYPES"
TIME_OF_FIRST_OBS_LABEL = "TIME OF FIRST OBS"
END_OF_HEADER_LABEL = "END OF HEADER"


def parse_number_with_exception(parse_function, arg, exception_msg: str):
    try:
        return parse_function(arg)
    except ValueError as exc:
        raise ValueError(exception_msg) from exc


def str2float(string: str, exception_msg: str):
    return parse_number_with_exception(float, string, exception_msg)


def str2int(string: str, exception_msg: str):
    return parse_number_with_exception(int, string, exception_msg)


def str2date(timestamp_str: str):
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")


supported_gnss = ['M', 'G', 'R', 'E', 'J', 'C', 'I', 'S']