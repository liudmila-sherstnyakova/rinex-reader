# RINEX Reader

## Introduction
This document describes RinexReader software, that was developed as part of author's master thesis at NMBU.
The application was written in Python, version 3.8. 
The purpose of this library is provide future users necessary tools to parse Rinex file 
and be able to  develop their own applications using obtained data.

## Prerequisites
Following packages are required for the script to run:
* numpy
* pytest
* psutil (used only for memory usage measurement in the demonstration script)

## Package Structure

* src/common
    - Contains common utility methods and [RinexData] class that represents the complete data set read from file
* src/navigation/v3
    - Contains classes and methods for reading Rinex ver 3 navigation files
* src/navigation/v4
    - Contains classes and methods for reading Rinex ver 4 navigation files
* src/observation/v3
    - Contains classes and methods for reading Rinex ver 3 observation files
* src/observation/v4
    - Contains classes and methods for reading Rinex ver 4 observation files
* src/[reader.py]
    - Contains method `read_rinex_file` that is the main method for reading Rinex files
    
Additionally, code base contains file [main.py], which provides some examples of library usage.

## Usage
### Entry point

In order to use RinexReader library, one will have to install it locally, e.g. using terminal:
```
$ pip install rinex-reader
```
After that read routing can be used inside a python script as follows:
```
from reader import read_rinex_file

result = read_rinex_file(rinex_file_path='path/to/file.22o')
```

### Input parameters

Read function takes following input parameters:
| Parameter name  | Required | Type                      | Description                                                                                                                                                                                                                                                                                                                                                                     |
|-----------------|----------|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| rinex_file_path | Yes      | String                    | Path to the Rinex file as string                                                                                                                                                                                                                                                                                                                                                |
| start_epoch     | No       | String or datetime        | Epoch time filter. Specifies start of the period that should be included in the result. <br />If specified, must be a datetime string in ISO8601 format, e.g. '2022-01-01T00:00:00'. <br />If used together with end_epoch, all blocks within the given timeframe will be read. <br />If used alone, the result will contain at most one block - the one that matches provided timestamp exactly. |
| end_epoch       | No       | String or datetime        | Epoch time filter. Specifies end of the period that should be included in the result.  <br />If specified, must be a datetime string in ISO8601 format, e.g. '2022-01-01T00:00:00'.  <br />When used, must be a date after the start_epoch date.                                                                                                                                            |
| gnss            | No       | List of strings           | GNSS filter. Specifies GNSS types (e.g. 'G' or 'E') that will be included into the result. All other GNSS will be ignored.                                                                                                                                                                                                                                                      |
| obs_types       | No       | String or list of strings | Observation types filter.  If a single string is provided, it is treated as regex and used to filter obs types for all satellites.  <br />If a list of strings is provided, then only that list is used to filter obs types.  <br />If a GNSS does not have any obs types from that list, then that GNSS is not included in the result.                                                     |
| verbose         | No       | Boolean                   | Flag to control debug output from the script. Set to True if debug output should be printed to console.                                                                                                                                                                                                                                                                         |

**Important note about filters:**
* gnss filter accepts values specified in Rinex format (see correct version specification):
    * G: GPS
    * R: GLONASS
    * E: Galileo
    * J: QZSS
    * C: BDS
    * I: NavIC/IRNSS S: SBAS payload 
* obs_types filter accepts values specified in Rinex format (see correct version specification)
    * Values consist of three parts:
        1. Type: C, L, D, S, X
        2. Band: Number between 0 and 9
        3. Attribute: A, B, C, D, E, I, L, M, N, P, Q, S, W, X, Y, Z
    * Example: C1C, L2X

### Output data structure

After the read is done, resulting variable will have following data structure:
```
result = read_rinex_file('path/to/file.22o')

result: {
		  'header': <header fields>,
		  'data': <observation record data>
	    }
```
#### Header
`result.header` object will contain all fields from the header. 
All the required fields will be accessible as separate objects, 
whereas non-required fields (for example, Rinex comments) will be gathered under other field.
```
result.header:
{
      "antenna": {
         "number": "1451-12216",
         "type": "TPSHIPER_VR     NONE",
         "height": 1.3142,
         "east": 0.0,
         "north": 0.0
      },
      "approximate_position": {
         "X": 3172507.4901,
         "Y": 603208.4428,
         "Z": 5481884.1614
      },
      "file_type": "O",
      "gnss": "M",
      "marker_name": "K004",
      "obs_types": {
         "R": ["C1C","L1C","D1C","C2C","L2C","D2C"],
         "E": ["C1X","L1X","D1X","C5X","L5X","D5X"],
		. . .
      },
      "other": {
         "COMMENT": "Win64 build Jun 01, 2022 (c) Topcon Positioning Systems | SRC: PPR3_290922.tps | OPT: -s 29092022d110000 -f 30092022d045959 -I 10 | OPT: -p PPR3_290922.ini | SN: 1451-12216 | 6480 EPOCHS",
		. . .
      },
      "system_time": "GPS",
      'time_of_first_observation":"2022-09-29T11:00:00.000000000",
      "version": 3.05
}
```
To access various fields, one can use following syntax:
```
antenna_h = result.header.antenna.height
rinex_version = result.header.version
rinex_comment = result.header.other['COMMENT']
```

#### Data

`result.data` object will contain a list of satellites that were present in the file and matched any given filter condition.
The structure will depend on the file type and version of the given file.

##### Observation V3 / V4
```
result.data:
{
      "satellites": {
         "R02": {
            "2022-09-29T11:00:00": [
               [23121980.8,-1,-1],
               [123470115.813,-1,6],
			. . .
            ]
         },
         "E01": {
            "2022-09-29T11:00:00": [
               [23121980.8,-1,-1],
               [123470115.813,-1,6],
			. . .
            ]
         }
      }
}
```
##### Navigation V3
```
result.data:
{
    "satellites": {
        "R02": {
            "2022-09-29T11:00:00": {
                SV_pos_X,
                URAI,
                msg_frame_time,
                ...
            }
        },
        "E01": {
            "2022-09-29T11:00:00": {
                Crs,
                omega,
                clock_bias,
                ...
            }
        }
    }
}
```
##### Navigation V4
```
result.data:
{
    "satellites": {
        "R02": {
            "2022-09-29T11:00:00": {
                SV_pos_X,
                URAI,
                msg_frame_time,
                ...
            }
        },
        "E01": {
            "2022-09-29T11:00:00": {
                Crs,
                omega,
                clock_bias,
                ...
            }
        }
    },
    "corrections": {
        "STO": {
            "R02": {
                "2022-09-29T11:00:00": {
                    time_offset,
                    A0,
                    ...
                }
            }
        },
        "EOP": {
            ...
        },
        "ION": {
            ...
        }
    }
}
```

## Examples
### Applying filters
Rinex reader allows to specify various filters to reduce time and memory needed to process the file,
however this is only applied to observation files. Navigation files are typically pretty small, 
so they are read as is without any filters. 

Here are some examples that demonstrate possible options
To read only desired GNSS from the file, use:
```
# use gnss filter to read only data for G and E systems
result = read_rinex_file(
	rinex_file_path="path/to/rinex/file",
	gnss=['G’,’E’]
)
```
To read only data observed at given timestamp, use
```
# use epoch time filter to read only data for given timestamp
result = read_rinex_file(
	rinex_file_path="path/to/rinex/file",
	start_epoch="2022-09-29T11:00:00",
)
```
To read data observed during a given interval, use
```
# use epoch time filter to read only data within a time interval
result = read_rinex_file(
	rinex_file_path="path/to/rinex/file",
	start_epoch="2022-09-29T11:00:00",
	end_epoch='2022-09-29T12:00:00'
)
```
To read data only for certain observation types, use 
```
# use obs_types filter to list desired observation types
result = read_rinex_file(
	rinex_file_path="path/to/rinex/file",
	obs_types=["C1C", "L1C"]
)

# use obs_types filter to specify regex to match several types
# use '.’ as wildcard character 
result = read_rinex_file(
	rinex_file_path="path/to/rinex/file",
	obs_types='.1.'
)
# result will contain data for all types that have band value = 1
```
Different filters can be combined together to achieve more precise result.

### Extracting values
To obtain a single value for the C1C type for satellite R02 at 2022-09-29T11:00:00, use
```
# C1C value for the R02 satellite observed at 2022-09-29T11:00:00:
val = result.data.satellites['R02']['2022-09-29T11:00:00']['C1C]['value']
# val = 23121980.8
```
To obtain SSI or LLI value for C1C type for the same satellite, use
```
# C1C SSI value for the R02 satellite observed at 2022-09-29T11:00:00:
ssi = result.data.satellites['R02']['2022-09-29T11:00:00']['C1C]['sis']
# ssi = -1, which means that there was no value in the file

# C1C LLI value for the R02 satellite observed at 2022-09-29T11:00:00:
lli = result.data.satellites['R02']['2022-09-29T11:00:00']['C1C]['lli']
# lli = -1, which means that there was no value in the file
```
It is possible to get all types for the given satellite for the given time
```
# All types for the R02 satellite observed at 2022-09-29T11:00:00:
R02 = result.data.satellites['R02']['2022-09-29T11:00:00']
# R02 = [(23121980.8, -1, -1),(…),(…)]
# Values have in the same order as listed in result.header.obs_types['R']
```
To use only values for observation types without corresponding SSI/LLI parameters, use
```
# List of obs_type values for the R02 satellite observed at T0:
all_values = list(map(lambda x: x["value"], result.data.satellites["R04"]["2022-09-29T11:00:00"])))
# all_values = [20279832.26, 108597600.752, 2741.776, 20279835.24, 84464829.352, 2132.492]
```
When handling navigation data, [RinexData] class provides utility method to search for the closest time block
for a given satellite
```
block = result.find_closest_match(sv='R02', timestamp='2022-09-29T11:00:00')
# block will contain fields based on the GNSS. In this example, one can use
# block.SV_pos_X or block.msg_frame_time, since GLONASS satellite was used.
```


[RinexData]: src/common/rinex_data.py
[reader.py]: src/reader.py
[main.py]: src/main.py