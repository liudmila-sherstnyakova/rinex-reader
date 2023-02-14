import time

import psutil  # memory measurement

from nmbu.rinex.reader import read_rinex_file


def read_without_filters():
    result = read_rinex_file(rinex_file_path="../data/29_1100_K004_18t.22o")
    print(result)
    print("C11 - L2I: ", result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["value"])
    print("C11 - L2I SSI: ", result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["ssi"])
    print("C11 - L2I LLI: ", result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["lli"])


def read_with_gnss_filter():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        gnss=["R", "C"]
    )
    print(result)
    print("C11: ", result.data.satellites["C11"]["2022-09-29T11:00:30"])
    print("R03: ", result.data.satellites["R03"]["2022-09-29T11:00:30"])


def read_with_obs_types_regex_filter():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        obs_types=".1C",
    )
    print(result)
    print("R04 - L1C: ", result.data.satellites["R04"]["2022-09-29T11:00:30"]["L1C"])
    print("R04 - D1C: ", result.data.satellites["R04"]["2022-09-29T11:00:30"]["D1C"])


def read_with_obs_types_list_filter():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        obs_types=["C1C", "L1C"],
    )
    print(result)
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:30"]["C1C"])
    print("R04 - L1C: ", result.data.satellites["R04"]["2022-09-29T11:00:30"]["L1C"])


def read_with_single_time_filter():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        start_epoch="2022-09-29T11:00:00",
    )
    print(result)
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:00"]["C1C"])
    print("R04 - C1C: ", list(map(lambda x: x["value"], result.data.satellites["R04"]["2022-09-29T11:00:00"])))
    print("E05 - C1X: ", result.data.satellites["E05"]["2022-09-29T11:00:00"]["C1X"])


def read_with_period_time_filter():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        start_epoch="2022-09-29T11:00:00",
        end_epoch="2022-09-29T11:00:40",
    )
    print(result)
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:00"]["C1C"])
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:10"]["C1C"])
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:20"]["C1C"])
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:30"]["C1C"])
    print("R04 - C1C: ", result.data.satellites["R04"]["2022-09-29T11:00:40"]["C1C"])


def read_nav_file():
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22p"
    )
    print(len(result.data.satellites))


if __name__ == '__main__':
    start_time = time.time()  # program start time
    # read_without_filters()
    # read_with_gnss_filter()
    # read_with_obs_types_regex_filter()
    # read_with_obs_types_list_filter()
    # read_with_single_time_filter()
    # read_with_period_time_filter()
    # read_nav_file()
    result = read_rinex_file("../data/k004_18t_rinex400_1.22p")
    print("--- Executed in %s seconds ---" % int((time.time() - start_time)))  # program total execution time
    print("--- Memory used: %f MB ---" % (psutil.Process().memory_info().rss / (1024 * 1024)))  # memory usage
