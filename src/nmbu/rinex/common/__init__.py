#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from datetime import datetime

RINEX_VERSION_TYPE_LABEL = "RINEX VERSION / TYPE"
MARKER_NAME_LABEL = "MARKER NAME"
ANTENNA_NO_TYPE_LABEL = "ANT # / TYPE"
ANTENNA_DELTA_HEN_LABEL = "ANTENNA: DELTA H/E/N"
APPROXIMATE_POSITION_LABEL = "APPROX POSITION XYZ"
SYS_NO_OBS_TYPES_LABEL = "SYS / # / OBS TYPES"
TIME_OF_FIRST_OBS_LABEL = "TIME OF FIRST OBS"
END_OF_HEADER_LABEL = "END OF HEADER"
PGM_RUNBY_DATE_LABEL = "PGM / RUN BY / DATE"
IONOSPHERIC_CORR_LABEL = "IONOSPHERIC CORR"
INTERVAL_LABEL = "INTERVAL"


def parse_number_with_exception(parse_function, arg, exception_msg: str):
    """
    Executes provided parse-function inside a try-catch block.
    If ValueError is raised, provided custom exception message is set on the exception.

    :param parse_function: function that will be executed inside try-catch
    :param arg: argument that will be used for parse_function
    :param exception_msg: custom exception message
    :return: result of the parse-function or ValueError
    """
    try:
        return parse_function(arg)
    except ValueError as exc:
        raise ValueError(exception_msg) from exc


def str2float(string: str, exception_msg: str):
    """
    Converts string to float. Raises ValueError with provided exception message when parsing fails.
    """
    return parse_number_with_exception(float, string, exception_msg)


def str2int(string: str, exception_msg: str):
    """
    Converts string to int. Raises ValueError with provided exception message when parsing fails.
    """
    return parse_number_with_exception(int, string, exception_msg)


def str2date(timestamp_str: str):
    """
    Converts string to datetime using ISO format: "%Y-%m-%dT%H:%M:%S".
    """
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")


def normalize_data_string(string: str) -> str:
    """
    Formats incoming Rinex data string to have length of 80 chars and removes first 4 spaces.
    """
    result = string.strip("\n")
    if len(result) < 80:
        result = result.ljust(80)
    if result.startswith("    "):
        result = result[4:]
    return result


supported_gnss = ['M', 'G', 'R', 'E', 'J', 'C', 'I', 'S']