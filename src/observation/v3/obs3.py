import datetime
import io
import itertools
from itertools import groupby, chain

import numpy as np
import xarray as xr

import common
from observation.v3.header import Header


class Observation:
    def __init__(self,
                 header: Header
                 ):
        self.header = header
        self.epochs = {}
        self.observations = 0
        self.all_satellites: set(str) = set()

    def check(self, line: str):
        print(line[:10])

    def checkSize(self, lines: [str], block_name: str):
        for gnns_system, obs_lines in groupby(lines, lambda x: x[0]):
            lines_in_group = list(obs_lines)
            sv_names = [name[:3] for name in lines_in_group]
            # self.all_satellites.update(n for n in sv_names)
            list_of_obs_types = self.header.obs_types_for_gnss(gnns_system).obs_types
            amount_of_obs_types = len(list_of_obs_types)
            complete_group = "".join(lines_in_group)
            result = np.genfromtxt(io.BytesIO(complete_group.encode("ascii")),
                          delimiter=(3,) + (14, 1, 1) * amount_of_obs_types,
                          usecols=range(1, 1 + 3 * amount_of_obs_types, 3),
                          names=list_of_obs_types  # column names. i.e. obs types
                          )
            if gnns_system in self.epochs.keys():
                self.epochs[gnns_system][block_name] = (sv_names, result)
            else:
                self.epochs[gnns_system]={block_name: (sv_names, result)}

    def checkSize2(self, lines: [str], block_name: str):
        for gnns_system, obs_lines in groupby(lines, lambda x: x[0]):
            lines_in_group = list(obs_lines)
            sv_names = [name[:3] for name in lines_in_group]
            self.all_satellites.update(n for n in sv_names)
            list_of_obs_types = self.header.obs_types_for_gnss(gnns_system).obs_types
            amount_of_obs_types = len(list_of_obs_types)
            complete_group = "".join(lines_in_group)
            result = np.genfromtxt(io.BytesIO(complete_group.encode("ascii")),
                          delimiter=(3,) + (14, 1, 1) * amount_of_obs_types,
                          usecols=chain([0],range(1, 1 + 3 * amount_of_obs_types, 3)),
                          names=["SV"] + list_of_obs_types,  # column names. i.e. obs types
                          dtype=["S3"] + ["f8"]*amount_of_obs_types
                          )
            """ result
            [(40058181.58, 2.08593454e+08,   137.145,         nan,          nan,       nan, 40058182.64, 1.61297678e+08, 106.05)
             (22609479.5 , 1.17733532e+08, -2011.596, 22609479.76, 88724463.489, -1515.947,         nan,            nan,    nan)
             (25094632.3 , 1.30674297e+08,  3227.674, 25094644.84, 98476694.993,  2432.389,         nan,            nan,    nan)
             (21623874.5 , 1.12601228e+08,   986.06 , 21623876.52, 84856774.506,   743.099,         nan,            nan,    nan)
             (25478726.16, 1.32674467e+08, -2710.344, 25478734.56, 99984020.619, -2042.526,         nan,            nan,    nan)]
            """
            """ sv_names
            ['C05', 'C27', 'C29', 'C30', 'C36']
            """
            """ block_name
            2022-09-30T04:59:50
            """
            if gnns_system in self.epochs.keys():
                self.epochs[gnns_system][block_name] = result
            else:
                self.epochs[gnns_system]={block_name: result}

    def read_epoch_line(self,
                        line: str
                        ) -> (str, bool, int):
        year = common.str2int(line[2:6], "Invalid year value in epoch line")
        month = common.str2int(line[7:9], "Invalid month value in epoch line")
        day = common.str2int(line[10:12], "Invalid day value in epoch line")
        hour = common.str2int(line[13:15], "Invalid hour value in epoch line")
        minute = common.str2int(line[16:18], "Invalid minute value in epoch line")
        full_seconds = common.str2float(line[19:29], "Invalid seconds value in epoch line")
        current_timestamp = datetime.datetime(year, month, day, hour, minute, int(full_seconds))

        epoch_flag = common.str2int(line[31:32], "Invalid value for epoch flag")
        block_size = common.str2int(line[32:35], "Invalid value for block size")

        return current_timestamp.isoformat(), epoch_flag == 0, block_size

    def read_block_line(self,
                        line: str,
                        block_name: str
                        ):
        satellite = line[0:3]
        obs_types = self.header.obs_types_for_gnss(satellite[0]).obs_types
        amount_of_obs_types = len(obs_types)
        observations = [np.genfromtxt(io.BytesIO(line[3: 16 * amount_of_obs_types].encode("ascii")),
                                      delimiter=(14, 1, 1) * amount_of_obs_types,
                                      usecols=range(0, 3 * amount_of_obs_types, 3))]
        """
        Idea: accumulate observations mapped to satellite name
        """

        # this line jumped from 20 sec to 104 sec
        data_array = xr.DataArray(name=block_name, data=observations, dims=["sv", "obs"],
                                  coords={"sv": [satellite], "obs": obs_types})


        # if block_name not in self.epochs.keys():
        #     self.epochs[block_name] = data_array
        # else:
        #     self.epochs[block_name] = xr.concat([self.epochs[block_name], data_array], dim="obs")
        """
        if len(data) == 0:
            data = epoch_data
        elif len(hdr["fields"]) == 1:  # one satellite system selected, faster to process
            data = xarray.concat((data, epoch_data), dim="time")
        else:  # general case, slower for different satellite systems all together
            data = xarray.merge((data, epoch_data))
        """
        self.epochs = xr.merge([self.epochs, data_array])
        # self.observations += 1

    def __repr__(self):
        return repr(self.header) + "\n" + repr(self.epochs)
