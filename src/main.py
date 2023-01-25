import io
import time

import psutil  # memory measurement

import common
from gnss import get_correct_gnss, GNSS
from observation.v3.header_v3 import read_header_block, RINEX_VERSION_TYPE_LABEL
from observation.v3.obs_v3 import read_all_observation_blocks


def __read_first_line(line: str) -> (float, str, GNSS):
    """
    Reads first line from RINEX file to determine version
    :param line: first line from RINEX file
    :return: tuple (RINEX version, file type, GNSS)
    """
    assert line[60:80] == RINEX_VERSION_TYPE_LABEL

    version = common.str2float(line[0:9], "Invalid version value in " + RINEX_VERSION_TYPE_LABEL)
    file_type = line[20]
    gnss = get_correct_gnss(line[40])
    return version, file_type, gnss


def read_rinex_file(filename: str):
    """
    Reads given RINEX file. It reads version and file type from the first header line
    and creates necessary objects to represent the data.

    Error is thrown if the given file is not a valid or supported RINEX format.

    :param filename: name of the input file
    :return: Object that contains header and body for the correct version and file type
    """
    rinex_file = io.open(filename)
    version, file_type, gnss = __read_first_line(rinex_file.readline())

    if version in (3.04, 3.05):
        if file_type == "O":
            header = read_header_block(rinex_file, version, file_type, gnss)
            observations = read_all_observation_blocks(rinex_file, header)
            return observations
        else:
            # TODO implement reading of nav files
            raise NotImplementedError("Navigation file type is not yet supported")

    elif version in (4.0,):
        # implement reading of RINEX 4
        raise NotImplementedError("Version 4.00 is not yet supported")

    else:
        raise ValueError("Unknown RINEX version. Expected 3.04|3.05|4.00, but got {v:.2f}".format(v=version))

    rinex_file.close()


# Example of usage with time/memory
if __name__ == '__main__':
    start_time = time.time()  # program start time
    result = read_rinex_file("../data/29_1100_K004_18t_1.22o")
    print(result.header)
  #  x = result.header.approximate_position["X"]
  #  y = result.header.approximate_position["Y"]
  #  z = result.header.approximate_position["Z"]
    print("--- Executed in %s seconds ---" % int((time.time() - start_time)))  # program total execution time
    print("--- Memory used: %f MB ---" % (psutil.Process().memory_info().rss / (1024 * 1024)))  # memory usage