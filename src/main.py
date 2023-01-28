import time

import psutil  # memory measurement

from reader import read_rinex_file

if __name__ == '__main__':
    start_time = time.time()  # program start time
    result = read_rinex_file(
        rinex_file_path="../data/29_1100_K004_18t.22o",
        gnss=["R", "C"],
        obs_types="..I",
        start_epoch="2022-09-29T11:00:00",
        end_epoch="2022-09-29T11:00:40",
        verbose=False
    )
    print(result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["value"])
    x = 2.0 * result.data.satellites["C11"]["2022-09-29T11:00:30"]["L2I"]["value"]
    print(x)
    print("--- Executed in %s seconds ---" % int((time.time() - start_time)))  # program total execution time
    print("--- Memory used: %f MB ---" % (psutil.Process().memory_info().rss / (1024 * 1024)))  # memory usage
