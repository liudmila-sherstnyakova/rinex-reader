import io
from observation.v3.obs3 import Observation as ObservationV3
from observation.v3.header import Header
import time
import psutil


if __name__ == '__main__':
    start_time = time.time()
    rinex_file = io.open("../data/29_1100_K004_18t_1.22o")
    # rinex_file = io.open("../data/testdata/ssir_12t.22o")
    reading_header = True
    header = Header(rinex_file.readline())

    # TODO choose correct reader based on version
    result = ObservationV3(header)
    current_block = None
    valid_block = True
    for line in rinex_file:
        if reading_header:
            reading_header = not header.read_line(line)
        else: # reading body
            if line.startswith('>'):
                current_block, valid_block, block_size = result.read_epoch_line(line)
                print("Working with block " + current_block)
                if valid_block:
                    block_lines = [next(rinex_file) for i in range(block_size) ]
                    if any(l.startswith('>') for l in block_lines):
                        raise ValueError("Block {name:s} has invalid size.".format(name=current_block))
                    block_lines.sort()
                    result.checkSize(block_lines, current_block)
            else:
                print("NOOP")
                # if valid_block:
                #     result.read_block_line(line, current_block)
    # result.observations = xr.merge(list(result.epochs.items()))
    print(result.epochs["C"]["2022-09-30T04:59:40"][0])
    print(result.epochs["C"]["2022-09-30T04:59:40"][1])
    print(result.epochs["C"]["2022-09-30T04:59:40"][1]["L2I"])
    """
    [(40058181.58, 2.08593454e+08,   137.145,         nan,          nan,       nan, 40058182.64, 1.61297678e+08, 106.05)
     (22609479.5 , 1.17733532e+08, -2011.596, 22609479.76, 88724463.489, -1515.947,         nan,            nan,    nan)
     (25094632.3 , 1.30674297e+08,  3227.674, 25094644.84, 98476694.993,  2432.389,         nan,            nan,    nan)
     (21623874.5 , 1.12601228e+08,   986.06 , 21623876.52, 84856774.506,   743.099,         nan,            nan,    nan)
     (25478726.16, 1.32674467e+08, -2710.344, 25478734.56, 99984020.619, -2042.526,         nan,            nan,    nan)]
    """
    print("---")
    print(result.epochs["C"].keys())
    rinex_file.close()
    print("--- Executed in %s seconds ---" % int((time.time() - start_time)))
    print("--- Memory used: %f MB ---" % (psutil.Process().memory_info().rss / (1024 * 1024)))
